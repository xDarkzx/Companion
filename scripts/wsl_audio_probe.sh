#!/usr/bin/env bash
# Quick WSLg audio probe for mic + speaker setup.
export PULSE_SERVER="${PULSE_SERVER:-unix:/mnt/wslg/PulseServer}"

echo "PULSE_SERVER=$PULSE_SERVER"
echo "--- pactl sinks (first 5 lines) ---"
pactl list sinks short 2>&1 | head -5
echo "--- pactl sources (first 5 lines) ---"
pactl list sources short 2>&1 | head -5
echo "--- sounddevice ---"
python3 <<'PY'
import sounddevice as sd
print('default device:', sd.default.device)
for i, dev in enumerate(sd.query_devices()):
    ins = dev.get('max_input_channels', 0)
    outs = dev.get('max_output_channels', 0)
    if ins or outs:
        print(f'  [{i}] in={ins} out={outs} {dev.get("name")}')
PY
