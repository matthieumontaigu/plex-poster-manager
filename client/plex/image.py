from typing import TypedDict


class PlexImage(TypedDict):
    key: str
    ratingKey: str
    thumb: str
    selected: str


def get_last_upload_if_agent_selected(
    images: list[PlexImage],
) -> PlexImage | None:
    """
    Returns the last uploaded image only if an agent image is currently selected and there is at least one uploaded image.
    This is used to determine what image to revert to when switching from agent to uploaded.

    :param images: List of Plex images
    :return: Last uploaded image if agent is selected, None otherwise
    """
    last_uploaded_image = None
    agent_is_selected = False

    for image in images:
        if is_uploaded(image):
            last_uploaded_image = image
        if is_selected(image) and is_from_agent(image):
            agent_is_selected = True

    return last_uploaded_image if agent_is_selected else None


def is_selected(image: PlexImage) -> bool:
    return image["selected"] == "1"


def is_from_agent(image: PlexImage) -> bool:
    return "tv.plex.agents.movie" in image["key"]


def is_uploaded(image: PlexImage) -> bool:
    return "upload" in image["key"]
