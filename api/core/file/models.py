from collections.abc import Mapping, Sequence
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator

from core.model_runtime.entities.message_entities import ImagePromptMessageContent
from core.tools.signature import sign_tool_file

from . import helpers
from .constants import FILE_MODEL_IDENTITY
from .enums import FileTransferMethod, FileType


class ImageConfig(BaseModel):
    """
    NOTE: This part of validation is deprecated, but still used in app features "Image Upload".
    """

    number_limits: int = 0
    transfer_methods: Sequence[FileTransferMethod] = Field(default_factory=list)
    detail: ImagePromptMessageContent.DETAIL | None = None


class FileUploadConfig(BaseModel):
    """
    File Upload Entity.
    """

    image_config: Optional[ImageConfig] = None
    allowed_file_types: Sequence[FileType] = Field(default_factory=list)
    allowed_file_extensions: Sequence[str] = Field(default_factory=list)
    allowed_file_upload_methods: Sequence[FileTransferMethod] = Field(default_factory=list)
    number_limits: int = 0


class File(BaseModel):
    # NOTE: dify_model_identity is a special identifier used to distinguish between
    # new and old data formats during serialization and deserialization.
    dify_model_identity: str = FILE_MODEL_IDENTITY

    id: Optional[str] = None  # message file id
    tenant_id: str
    type: FileType
    transfer_method: FileTransferMethod
    # If `transfer_method` is `FileTransferMethod.remote_url`, the
    # `remote_url` attribute must not be `None`.
    remote_url: Optional[str] = None  # remote url
    # If `transfer_method` is `FileTransferMethod.local_file` or
    # `FileTransferMethod.tool_file`, the `related_id` attribute must not be `None`.
    #
    # It should be set to `ToolFile.id` when `transfer_method` is `tool_file`.
    related_id: Optional[str] = None
    filename: Optional[str] = None
    extension: Optional[str] = Field(default=None, description="File extension, should contain dot")
    mime_type: Optional[str] = None
    size: int = -1

    # Those properties are private, should not be exposed to the outside.
    _storage_key: str

    def __init__(
        self,
        *,
        id: Optional[str] = None,
        tenant_id: str,
        type: FileType,
        transfer_method: FileTransferMethod,
        remote_url: Optional[str] = None,
        related_id: Optional[str] = None,
        filename: Optional[str] = None,
        extension: Optional[str] = None,
        mime_type: Optional[str] = None,
        size: int = -1,
        storage_key: Optional[str] = None,
        dify_model_identity: Optional[str] = FILE_MODEL_IDENTITY,
        url: Optional[str] = None,
    ):
        super().__init__(
            id=id,
            tenant_id=tenant_id,
            type=type,
            transfer_method=transfer_method,
            remote_url=remote_url,
            related_id=related_id,
            filename=filename,
            extension=extension,
            mime_type=mime_type,
            size=size,
            dify_model_identity=dify_model_identity,
            url=url,
        )
        self._storage_key = str(storage_key)

    def to_dict(self) -> Mapping[str, str | int | None]:
        data = self.model_dump(mode="json")
        return {
            **data,
            "url": self.generate_url(),
        }

    @property
    def markdown(self) -> str:
        url = self.generate_url()
        if self.type == FileType.IMAGE:
            text = f"![{self.filename or ''}]({url})"
        else:
            text = f"[{self.filename or url}]({url})"

        return text

    def generate_url(self) -> Optional[str]:
        if self.transfer_method == FileTransferMethod.REMOTE_URL:
            return self.remote_url
        elif self.transfer_method == FileTransferMethod.LOCAL_FILE:
            if self.related_id is None:
                raise ValueError("Missing file related_id")
            return helpers.get_signed_file_url(upload_file_id=self.related_id)
        elif self.transfer_method == FileTransferMethod.TOOL_FILE:
            assert self.related_id is not None
            assert self.extension is not None
            return sign_tool_file(tool_file_id=self.related_id, extension=self.extension)

    def to_plugin_parameter(self) -> dict[str, Any]:
        return {
            "dify_model_identity": FILE_MODEL_IDENTITY,
            "mime_type": self.mime_type,
            "filename": self.filename,
            "extension": self.extension,
            "size": self.size,
            "type": self.type,
            "url": self.generate_url(),
        }

    @model_validator(mode="after")
    def validate_after(self):
        match self.transfer_method:
            case FileTransferMethod.REMOTE_URL:
                if not self.remote_url:
                    raise ValueError("Missing file url")
                if not isinstance(self.remote_url, str) or not self.remote_url.startswith("http"):
                    raise ValueError("Invalid file url")
            case FileTransferMethod.LOCAL_FILE:
                if not self.related_id:
                    raise ValueError("Missing file related_id")
            case FileTransferMethod.TOOL_FILE:
                if not self.related_id:
                    raise ValueError("Missing file related_id")
        return self
