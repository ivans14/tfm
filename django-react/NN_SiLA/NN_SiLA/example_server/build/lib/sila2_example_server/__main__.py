# Generated by sila2.code_generator; sila2.__version__: 0.9.2
import logging
import signal
from typing import Optional
from uuid import UUID

import typer
from typer import BadParameter, Option

from sila2.framework.utils import running_in_docker

from .server import Server

logger = logging.getLogger(__name__)


def main(
    ip_address: str = Option(
        "0.0.0.0" if running_in_docker() else "127.0.0.1", "-a", "--ip-address", help="The IP address"
    ),
    port: int = Option(50052, "-p", "--port", help="The port"),
    server_uuid: Optional[str] = Option(
        None, "--server-uuid", help="The server UUID [default: generate]", show_default=False
    ),
    disable_discovery: bool = Option(False, "--disable-discovery", help="Disable SiLA Server Discovery"),
    insecure: bool = Option(False, "--insecure", help="Start without encryption"),
    private_key_file: Optional[str] = Option(
        None, "-k", "--private-key-file", help="Private key file (e.g. 'server-key.pem')"
    ),
    cert_file: Optional[str] = Option(None, "-c", "--cert-file", help="Certificate file (e.g. 'server-cert.pem')"),
    ca_file_for_discovery: Optional[str] = Option(
        None,
        "--ca-file-for-discovery",
        help="Certificate Authority file for distribution via the SiLA Server Discovery (e.g. 'server-ca.pem')",
    ),
    ca_export_file: Optional[str] = Option(
        None, help="When using a self-signed certificate, write the generated CA to this file"
    ),
    quiet: bool = Option(False, "--quiet", help="Only log errors"),
    verbose: bool = Option(False, "--verbose", help="Enable verbose logging"),
    debug: bool = Option(False, "--debug", help="Enable debug logging"),
):
    # validate parameters
    if (insecure or ca_export_file is not None) and (cert_file is not None or private_key_file is not None):
        raise BadParameter("Cannot use --insecure or --ca-export-file with --private-key-file or --cert-file")
    if (cert_file is None and private_key_file is not None) or (private_key_file is None and cert_file is not None):
        raise BadParameter("Either provide both --private-key-file and --cert-file, or none of them")
    if insecure and ca_export_file is not None:
        raise BadParameter("Cannot use --export-ca-file with --insecure")

    # prepare server parameters
    cert = open(cert_file, "rb").read() if cert_file is not None else None
    private_key = open(private_key_file, "rb").read() if private_key_file is not None else None
    ca_for_discovery = open(ca_file_for_discovery, "rb").read() if ca_file_for_discovery is not None else None
    parsed_server_uuid = UUID(server_uuid) if server_uuid is not None else None

    # logging setup
    initialize_logging(quiet=quiet, verbose=verbose, debug=debug)

    # run server
    server = Server(server_uuid=parsed_server_uuid)
    try:
        if insecure:
            server.start_insecure(ip_address, port, enable_discovery=not disable_discovery)
        else:
            server.start(
                ip_address,
                port,
                cert_chain=cert,
                private_key=private_key,
                enable_discovery=not disable_discovery,
                ca_for_discovery=ca_for_discovery,
            )
            if ca_export_file is not None:
                with open(ca_export_file, "wb") as fp:
                    fp.write(server.generated_ca)
                logger.info(f"Wrote generated CA to '{ca_export_file}'")
        logger.info("Server startup compleete")

        signal.signal(signal.SIGTERM, lambda *args: server.stop())

        try:
            server.grpc_server.wait_for_termination()
        except KeyboardInterrupt:
            pass
    finally:
        if server.running:
            server.stop()
        logger.info("Server shutdown complete")


def initialize_logging(*, quiet: bool = False, verbose: bool = False, debug: bool = False):
    if sum((quiet, verbose, debug)) > 1:
        raise BadParameter("--quiet, --verbose and --debug are mutually exclusive")

    level = logging.WARNING
    if verbose:
        level = logging.INFO
    if debug:
        level = logging.DEBUG
    if quiet:
        level = logging.ERROR

    logging.basicConfig(level=level, format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
    logger.setLevel(logging.INFO)
    logging.getLogger("xmlschema").setLevel(logging.WARNING)


if __name__ == "__main__":
    typer.run(main)
