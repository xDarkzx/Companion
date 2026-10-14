"""Service contracts: every ROS service a node offers or calls is registered, and vice versa."""
from __future__ import annotations

from pathlib import Path
import sys

_TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(_TOOLS))

from companion_contracts import SERVICE_CONTRACTS, ServiceContract  # noqa: E402
from validate_companion_architecture import (  # noqa: E402
    ros_src,
    scan_services,
    validate_services,
)


def write_node(tmp_path: Path, package: str, body: str) -> Path:
    module = tmp_path / package / package
    module.mkdir(parents=True)
    path = module / 'probe_node.py'
    path.write_text(body, encoding='utf-8')
    return path


def test_scan_finds_servers_and_clients_through_constants(tmp_path):
    path = write_node(
        tmp_path,
        'companion_perception',
        "FIND_SERVICE = '/companion/find_object'\n"
        'self.create_service(FindObject, FIND_SERVICE, self._on_find)\n'
        "self.create_client(FindObject, '/companion/other')\n",
    )
    servers, clients = scan_services(path)
    assert servers == [('FindObject', '/companion/find_object')]
    assert clients == [('FindObject', '/companion/other')]


def test_an_unregistered_service_is_reported(tmp_path):
    write_node(
        tmp_path,
        'companion_perception',
        "self.create_service(FindObject, '/companion/unknown', self._cb)\n",
    )
    errors = validate_services(tmp_path, contracts={})
    assert any("undocumented service '/companion/unknown'" in e for e in errors)


def test_a_server_in_the_wrong_package_is_reported(tmp_path):
    write_node(
        tmp_path,
        'companion_agent',
        "self.create_service(FindObject, '/companion/find_object', self._cb)\n",
    )
    contracts = {
        '/companion/find_object': ServiceContract(
            srv_type='FindObject',
            servers=frozenset({'companion_perception'}),
            clients=frozenset(),
        ),
    }
    errors = validate_services(tmp_path, contracts=contracts)
    assert any('may not serve' in e for e in errors)


def test_a_registered_service_without_a_server_is_reported(tmp_path):
    (tmp_path / 'companion_perception').mkdir()
    contracts = {
        '/companion/find_object': ServiceContract(
            srv_type='FindObject',
            servers=frozenset({'companion_perception'}),
            clients=frozenset(),
        ),
    }
    errors = validate_services(tmp_path, contracts=contracts)
    assert any('has no server' in e for e in errors)


def test_the_real_codebase_matches_the_service_contracts():
    assert '/companion/find_object' in SERVICE_CONTRACTS
    assert validate_services(ros_src(), contracts=SERVICE_CONTRACTS) == []
