# Generated by sila2.code_generator; sila2.__version__: 0.10.1
# -----
# This class does not do anything useful at runtime. Its only purpose is to provide type annotations.
# Since sphinx does not support .pyi files (yet?), so this is a .py file.
# -----

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable, List, Optional

    from labwaretransfersiteurcontroller_types import (
        LabwareDelivered_Responses,
        LabwareRemoved_Responses,
        PrepareForInput_Responses,
        PrepareForOutput_Responses,
    )
    from sila2.client import ClientMetadataInstance, ClientObservableCommandInstance, ClientUnobservableProperty

    from .labwaretransfersiteurcontroller_types import HandoverPosition, PositionIndex


class LabwareTransferSiteURControllerClient:
    """

    This feature (together with the "Labware Transfer Manipulator Controller" feature) provides commands to trigger the
    sub tasks of handing over a labware item, e.g. a microtiter plate, from one device to another in a standardized and
    generic way.

    For each labware transfer a defined sequence of commands has to be called on both involved devices to ensure the
    proper synchronization of all necessary transfer actions without unwanted physical interferences and to optimize
    the transfer performance regarding the execution time. Using the generic commands labware transfers between any
    arbitrary labware handling devices can be controlled (a robot device has not necessarily be involved).

    Generally a labware transfer is executed between a source and a destination device, where one of them is the
    active device (executing the actual handover actions) and the other one is the passive device.

    The "Labware Transfer Site Controller" feature is used to control the labware transfer on the side of the
    passive device to hand over a labware to or taking over a labware from an active device, which provides the
    "Labware Transfer Manipulator Controller" feature.

    If a device is capable to act either as the active or as the passive device of a labware transfer it must provide
    both features.

    The complete sequence of issued transfer commands on both devices is as follows:

    1. Prior to the actual labware transfer a "Prepare For Output" command is sent to the source device to execute all
       necessary actions to be ready to release a labware item (e.g. open a tray) and simultaneously a "Prepare For
       Input" command is sent to the destination device to execute all necessary actions to be ready to receive a
       labware item (e.g. position the robotic arm near the tray of the source device).
    2. When both devices have successfully finished their "Prepare For ..." command execution, the next commands are
       issued.
    3a If the source device is the active device it will receive a "Put Labware" command to execute all necessary
       actions to put the labware item to the destination device. After the transfer has been finished successfully the
       destination device receives a "Labware Delivered" command, that triggers all actions to be done after the
       labware item has been transferred (e.g. close the opened tray).
    3b If the destination device is the active device it will receive a "Get Labware" command to execute all necessary
       actions to get the labware from the source device (e.g. gripping the labware item). After that command has been
       finished successfully the source device receives a "Labware Removed" command, that triggers all actions to be
       done after the labware item has been transferred (e.g. close the opened tray).

    The command sequences for a passive source or destination device have always to be as follows:
    - for a passive source device:        PrepareForOutput - LabwareRemoved
    - for a passive destination device:   PrepareForInput - LabwareDelivered

    If the commands issued by the client differ from the respective command sequences a "Invalid Command Sequence"
    error will be raised.

    To address the location, where a labware item can be handed over to or from other devices, every device must
    provide one or more uniquely named positions (handover positions) via the "Available Handover Positions" property.
    A robot usually has got at least one handover position for each other device that it interacts with, whereas the
    most none-transport devices will only have one handover position.
    In case of a position array (e.g. a rack) the position within the array is specified via the sub position of the
    handover position, passed as index number.

    To address the positions within a device where the transferred labware item has to be stored at or is to be taken
    from (e.g. the storage positions inside an incubator), the internal position can be specified. Each device must
    provide the the number of available internal positions via the "Number Of Internal Positions" property.

    With the "Prepare For Input" command there is also information about the labware transferred, like labware type or
    a unique labware identifier (e.g. a barcode).

    """

    AvailableHandoverPositions: ClientUnobservableProperty[List[HandoverPosition]]
    """
    All handover positions of the device including the number of sub positions
    """

    NumberOfInternalPositions: ClientUnobservableProperty[int]
    """
    The number of addressable internal positions of the device
    """

    def PrepareForInput(
        self,
        HandoverPosition: HandoverPosition,
        InternalPosition: PositionIndex,
        LabwareType: str,
        LabwareUniqueID: str,
        *,
        metadata: Optional[Iterable[ClientMetadataInstance]] = None,
    ) -> ClientObservableCommandInstance[PrepareForInput_Responses]:
        """
        Put the device into a state where it is ready to accept new labware at the specified handover position.
        """
        ...

    def PrepareForOutput(
        self,
        HandoverPosition: HandoverPosition,
        InternalPosition: PositionIndex,
        *,
        metadata: Optional[Iterable[ClientMetadataInstance]] = None,
    ) -> ClientObservableCommandInstance[PrepareForOutput_Responses]:
        """
        Put the device into a state where it is ready to release the labware at the specified handover position.
        """
        ...

    def LabwareDelivered(
        self, HandoverPosition: HandoverPosition, *, metadata: Optional[Iterable[ClientMetadataInstance]] = None
    ) -> ClientObservableCommandInstance[LabwareDelivered_Responses]:
        """
        Notifies the passive destination device of a labware item that has been transferred to it (sent after a "PrepareForInput" command).
        """
        ...

    def LabwareRemoved(
        self, HandoverPosition: HandoverPosition, *, metadata: Optional[Iterable[ClientMetadataInstance]] = None
    ) -> ClientObservableCommandInstance[LabwareRemoved_Responses]:
        """
        Notifies the passive source device of a labware item that has been removed from it (sent after a "PrepareForOutput" command).
        """
        ...
