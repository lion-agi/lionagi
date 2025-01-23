from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BrowserAction(str, Enum):
    """
    Basic web actions:
      - 'open_url': Retrieve HTML/text from URL
      - 'download_file': Download from URL -> local path
      - 'screenshot': (Optional) capture screenshot
      - 'click_element': (Optional) simulate click by CSS/xpath
    """

    open_url = "open_url"
    download_file = "download_file"
    screenshot = "screenshot"
    click_element = "click_element"


class BrowserRequest(BaseModel):
    """
    Request for BrowserTool.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "BrowserTool: Allows basic web interactions, reading content, "
                "downloading, or simple element clicks."
            )
        }
    )

    action: BrowserAction
    url: Optional[str] = Field(
        None,
        description="For 'open_url','download_file'. The target web address.",
    )
    local_path: Optional[str] = Field(
        None, description="For 'download_file'. Where to save locally."
    )
    selector: Optional[str] = Field(
        None,
        description="For 'click_element' or 'screenshot' partial region. A CSS or Xpath expression.",
    )
    full_page: bool = Field(
        False,
        description="For 'screenshot'. If True, capture entire page, else only viewport.",
    )


class BrowserResponse(BaseModel):
    """
    Response from BrowserTool.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "BrowserTool Response: Contains page content, downloaded file path, screenshot data, etc."
            )
        }
    )

    success: bool
    error: Optional[str] = Field(
        None, description="If success=False, reason for failure."
    )
    page_content: Optional[str] = None
    saved_path: Optional[str] = None
    screenshot_data: Optional[bytes] = None
    click_result: Optional[str] = None
