"""Parametric coupons for the servo-routed 2+1 fan manifold."""

from .parameters import RoutingCouponParameters, load_routing_parameters
from .coupons import (
    build_linkage_coupon,
    build_shaft_clearance_coupon,
    build_seal_gap_coupon,
)
from .interfaces import build_p12_fan_pod, build_core_routing_adapter
from .prototype_parameters import RoutingPrototypeParameters, load_routing_prototype_parameters
from .v03_parameters import RoutingV03Parameters, load_routing_v03_parameters
from .v03 import (
    build_full_area_t_diverter_body,
    build_t_diverter_flap_blank,
    build_exhaust_fan_square_transition,
)
from .prototype import (
    build_fan_rect_transition,
    build_supply_merge_collector,
    build_double_diverter_body,
    build_diverter_flap_blank,
)

__all__ = [
    "RoutingCouponParameters",
    "load_routing_parameters",
    "build_linkage_coupon",
    "build_shaft_clearance_coupon",
    "build_seal_gap_coupon",
    "build_p12_fan_pod",
    "build_core_routing_adapter",
    "RoutingPrototypeParameters",
    "load_routing_prototype_parameters",
    "RoutingV03Parameters",
    "load_routing_v03_parameters",
    "build_full_area_t_diverter_body",
    "build_t_diverter_flap_blank",
    "build_exhaust_fan_square_transition",
    "build_fan_rect_transition",
    "build_supply_merge_collector",
    "build_double_diverter_body",
    "build_diverter_flap_blank",
]
