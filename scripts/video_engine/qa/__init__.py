"""Quality assurance gates."""
from .pre_render import validate_pre_render
from .post_render import validate_post_render

__all__ = ["validate_pre_render", "validate_post_render"]
