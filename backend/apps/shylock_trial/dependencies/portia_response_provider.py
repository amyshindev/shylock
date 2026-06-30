from fastapi import Depends

from shylock_trial.adapter.outbound.client.portia_response_client import PortiaResponseClient
from shylock_trial.app.ports.input.portia_response_use_case import PortiaResponseUseCase
from shylock_trial.app.ports.output.portia_response_port import PortiaResponsePort
from shylock_trial.app.use_cases.portia_response_interactor import PortiaResponseInteractor


def get_portia_response_port() -> PortiaResponsePort:
    return PortiaResponseClient()


def get_portia_response_use_case(
    port: PortiaResponsePort = Depends(get_portia_response_port),
) -> PortiaResponseUseCase:
    return PortiaResponseInteractor(port=port)
