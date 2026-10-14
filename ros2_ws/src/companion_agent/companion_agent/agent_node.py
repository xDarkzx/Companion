"""Voice/text command router — multi-step plans, memory-aware, RAG state."""
from pathlib import Path

from companion_agent.conversational_reply import conversational_reply, reply_for_plan
from companion_agent.fact_recall import try_recall_reply
from companion_agent.parse_command import CommandStep, parse_command
from companion_agent.remember_command import parse_remember_fact
from companion_agent.reply_templates import boot_greeting_text
from companion_agent.vision_react import hint_to_step, should_react_to_hint
from companion_interfaces.msg import AgentState, BehaviorRequest
from companion_memory.fact_store import FactStore
from companion_memory.places_store import list_place_names
from companion_memory.rag_retriever import retrieve_context
from companion_memory.session_buffer import SessionBuffer
from companion_voice.reply_catalog import phrase_text
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

COMMAND_TOPIC = '/companion/voice_command'
BEHAVIOR_TOPIC = '/companion/behavior_request'
STATE_TOPIC = '/companion/agent_state'
TTS_TOPIC = '/companion/tts_request'
NAV_STATUS_TOPIC = '/companion/nav_status'
DETECTION_HINT_TOPIC = '/companion/detection_hint'
QUEUE_DEPTH = 10
_NAV_BEHAVIORS = frozenset({'go_to_place', 'go_home'})


class AgentNode(Node):
    """Convert text commands into ordered BehaviorRequest messages."""

    def __init__(self) -> None:
        """Declare params, load place names, wire topics."""
        super().__init__('agent_node')
        self.declare_parameter('default_intensity', 0.85)
        self.declare_parameter('places_file', '')
        self.declare_parameter('people_file', '')
        self.declare_parameter('step_delay_sec', 4.0)
        self.declare_parameter('llm_provider', 'none')
        self.declare_parameter('ollama_model', 'llama3.2')
        self.declare_parameter('ollama_base_url', 'http://127.0.0.1:11434')
        self.declare_parameter('speak_replies', True)
        self.declare_parameter('wait_for_nav', True)
        self.declare_parameter('session_max_turns', 20)
        self.declare_parameter('react_to_vision', False)
        self.declare_parameter('vision_hint_cooldown_sec', 8.0)
        self.declare_parameter('fact_db_path', '')
        self.declare_parameter('max_stored_facts', 500)
        self.declare_parameter('welcome_message', '')

        self._intensity = float(self.get_parameter('default_intensity').value)
        self._step_delay = float(self.get_parameter('step_delay_sec').value)
        self._provider = str(self.get_parameter('llm_provider').value)
        self._ollama_model = str(self.get_parameter('ollama_model').value)
        self._ollama_base_url = str(self.get_parameter('ollama_base_url').value)
        self._speak_replies = bool(self.get_parameter('speak_replies').value)
        self._wait_for_nav = bool(self.get_parameter('wait_for_nav').value)
        self._react_to_vision = bool(self.get_parameter('react_to_vision').value)
        self._vision_cooldown = float(self.get_parameter('vision_hint_cooldown_sec').value)
        self._last_vision_hint_at = 0.0
        self._places_file = Path(self.get_parameter('places_file').value)
        self._people_file = Path(self.get_parameter('people_file').value)
        self._known_places = list_place_names(self._places_file)
        self._session = SessionBuffer(int(self.get_parameter('session_max_turns').value))
        fact_path = str(self.get_parameter('fact_db_path').value).strip()
        self._facts: FactStore | None = None
        if fact_path:
            self._facts = FactStore(
                Path(fact_path),
                int(self.get_parameter('max_stored_facts').value),
            )

        self._behavior_pub = self.create_publisher(
            BehaviorRequest, BEHAVIOR_TOPIC, QUEUE_DEPTH
        )
        self._state_pub = self.create_publisher(AgentState, STATE_TOPIC, QUEUE_DEPTH)
        self._tts_pub = self.create_publisher(String, TTS_TOPIC, QUEUE_DEPTH)
        self.create_subscription(String, COMMAND_TOPIC, self._on_command, QUEUE_DEPTH)
        self.create_subscription(String, NAV_STATUS_TOPIC, self._on_nav_status, QUEUE_DEPTH)
        self.create_subscription(
            String, DETECTION_HINT_TOPIC, self._on_detection_hint, QUEUE_DEPTH
        )

        self._pending_steps: list[CommandStep] = []
        self._waiting_for_nav = False
        self._step_timer = self.create_timer(self._step_delay, self._run_next_step)
        self._step_timer.cancel()

        welcome = str(self.get_parameter('welcome_message').value).strip()
        self._welcome_timer = None
        if self._speak_replies:
            self._welcome_text = welcome
            self._welcome_timer = self.create_timer(2.0, self._speak_welcome_once)

        names = ', '.join(sorted(self._known_places)) or '(none)'
        self.get_logger().info(
            f'AgentNode on {COMMAND_TOPIC}; places: {names}; llm={self._provider}'
        )
        self._publish_state('idle', status_text='ready')

    def _on_command(self, msg: String) -> None:
        """Parse text, run memory lookup, queue a behavior plan."""
        prior_history = self._session.recent(10)
        self._session.add_user(msg.data)
        self._publish_state('listening', status_text=msg.data[:40])

        remember = parse_remember_fact(msg.data)
        if remember is not None:
            self._handle_remember(remember)
            return

        rag_used, memory_count, summary = retrieve_context(
            msg.data, self._places_file, self._people_file, self._facts
        )
        session_note = self._session.summary(limit=2)
        if session_note:
            summary = f'{summary}; {session_note}' if summary else session_note
            memory_count += len(self._session.recent(2))
            rag_used = True
        self._publish_state(
            'retrieving',
            rag_used=rag_used,
            memory_count=memory_count,
            status_text=summary or 'scanning memory',
        )

        plan = parse_command(msg.data, self._known_places)
        if plan is None:
            recall = try_recall_reply(msg.data, self._facts)
            if recall is not None:
                self._publish_state(
                    'speaking',
                    rag_used=True,
                    memory_count=memory_count or 1,
                    status_text=summary or 'recalling fact',
                )
                self._speak(
                    conversational_reply(
                        self._provider,
                        msg.data,
                        summary,
                        recall,
                        self._ollama_model,
                        self._ollama_base_url,
                        history=prior_history,
                    )
                )
                self._publish_state(
                    'idle',
                    rag_used=True,
                    memory_count=memory_count or 1,
                    status_text='ready',
                )
                self.get_logger().info(f'Recalled fact for: {msg.data!r}')
                return

            self._publish_state(
                'error',
                status_text='did not understand',
            )
            self._speak(
                conversational_reply(
                    self._provider,
                    msg.data,
                    summary,
                    phrase_text('dont_understand'),
                    self._ollama_model,
                    self._ollama_base_url,
                    history=prior_history,
                )
            )
            self._publish_state('idle', status_text='ready')
            self.get_logger().info(f'Unrecognized command: {msg.data!r}')
            return

        self._publish_state(
            'thinking',
            rag_used=rag_used,
            memory_count=memory_count,
            status_text=summary or 'planning',
        )

        if plan.steps and plan.steps[0].behavior == 'stop':
            self._pending_steps.clear()
            self._step_timer.cancel()
            self._publish_state('acting', status_text='stop')
            self._speak(phrase_text('stop'))
            self._publish_step(plan.steps[0])
            self._publish_state('idle', status_text='ready')
            return

        self._pending_steps = list(plan.steps)
        self.get_logger().info(
            f'Plan {[s.behavior for s in plan.steps]} from {msg.data!r}'
        )
        self._speak(
            reply_for_plan(
                self._provider,
                msg.data,
                plan,
                summary,
                self._ollama_model,
                self._ollama_base_url,
                history=prior_history,
            )
        )
        self._publish_state('acting', status_text='executing')
        self._run_next_step()

    def _handle_remember(self, fact_text: str) -> None:
        """Persist a user fact when Tier 3 memory is enabled."""
        self._publish_state('retrieving', rag_used=True, status_text='storing fact')
        if self._facts is None:
            self._speak(phrase_text('memory_off'))
            self._publish_state('error', status_text='no fact db')
            self._publish_state('idle', status_text='ready')
            return
        stamp = self.get_clock().now().nanoseconds / 1e9
        self._facts.add(fact_text, stamp)
        self._speak(
            conversational_reply(
                self._provider,
                f'remember that {fact_text}',
                f'stored fact: {fact_text}',
                phrase_text('remember_ok'),
                self._ollama_model,
                self._ollama_base_url,
                history=self._session.recent(10),
            )
        )
        self._publish_state(
            'idle',
            rag_used=True,
            memory_count=self._facts.count(),
            status_text=f'stored: {fact_text[:40]}',
        )
        self.get_logger().info(f'Remembered fact: {fact_text!r}')

    def _speak_welcome_once(self) -> None:
        """Greet the user once at startup (desktop prototype)."""
        if self._welcome_timer is not None:
            self._welcome_timer.cancel()
        if self._welcome_text.strip().lower() == 'random':
            self._speak(boot_greeting_text())
        elif self._welcome_text:
            self._speak(self._welcome_text)
        else:
            self._speak(boot_greeting_text())
        self._publish_state('idle', status_text='ready')

    def _on_detection_hint(self, msg: String) -> None:
        """Optionally trigger follow/harass from vision when the agent is idle."""
        now = self.get_clock().now().nanoseconds / 1e9
        cooldown_ok = (now - self._last_vision_hint_at) >= self._vision_cooldown
        if not should_react_to_hint(
            msg.data,
            react_enabled=self._react_to_vision,
            has_pending_steps=bool(self._pending_steps),
            waiting_for_nav=self._waiting_for_nav,
            cooldown_elapsed=cooldown_ok,
        ):
            return

        step = hint_to_step(msg.data)
        if step is None:
            return

        self._last_vision_hint_at = now
        self._publish_state('acting', status_text=f'vision:{step.behavior}')
        self._publish_step(step, source='vision')
        self._publish_state('idle', status_text='ready')
        self.get_logger().info(f'Vision hint -> {step.behavior}')

    def _run_next_step(self) -> None:
        """Publish the next step in the queue."""
        if not self._pending_steps:
            self._step_timer.cancel()
            self._waiting_for_nav = False
            self._publish_state('idle', status_text='ready')
            return

        step = self._pending_steps.pop(0)
        self._publish_step(step)

        if not self._pending_steps:
            self._step_timer.cancel()
            self._waiting_for_nav = False
            self._publish_state('idle', status_text='ready')
            return

        if step.behavior in _NAV_BEHAVIORS and self._wait_for_nav:
            self._waiting_for_nav = True
            self._step_timer.cancel()
        else:
            self._waiting_for_nav = False
            self._step_timer.reset()

    def _on_nav_status(self, msg: String) -> None:
        """Advance the plan after Nav2 reports arrival or failure."""
        if not self._waiting_for_nav:
            return
        status = msg.data.strip().lower()
        if status not in {'arrived', 'failed'}:
            return

        self._waiting_for_nav = False
        if status == 'failed':
            self._pending_steps.clear()
            self._step_timer.cancel()
            self._speak(phrase_text('nav_failed'))
            self._publish_state('idle', status_text='nav failed')
            return

        self._run_next_step()

    def _publish_step(self, step: CommandStep, source: str = 'voice') -> None:
        """Emit one BehaviorRequest for a plan step."""
        req = BehaviorRequest()
        req.header.stamp = self.get_clock().now().to_msg()
        req.behavior = step.behavior
        req.target = step.target
        req.source = source
        req.intensity = self._intensity
        self._behavior_pub.publish(req)
        self.get_logger().info(
            f'Step -> {step.behavior} target={step.target!r}'
        )

    def _speak(self, text: str) -> None:
        """Publish a TTS request when voice replies are enabled."""
        cleaned = text.strip()
        if not self._speak_replies or not cleaned:
            return
        self._publish_state('speaking', status_text=cleaned[:40])
        msg = String()
        msg.data = cleaned
        self._tts_pub.publish(msg)
        self._session.add_assistant(cleaned)

    def _publish_state(
        self,
        state: str,
        rag_used: bool = False,
        memory_count: int = 0,
        status_text: str = '',
    ) -> None:
        """Publish AgentState for face overlay and logs."""
        msg = AgentState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.state = state
        msg.provider = self._provider if state in {
            'retrieving', 'thinking', 'speaking',
        } else 'none'
        msg.rag_used = rag_used
        msg.memory_count = memory_count
        msg.status_text = status_text
        self._state_pub.publish(msg)


def main(args=None) -> None:
    """Spin with clean shutdown."""
    rclpy.init(args=args)
    node = AgentNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if getattr(node, '_facts', None) is not None:
            node._facts.close()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
