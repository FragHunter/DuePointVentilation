"""Parametric coupons for the servo-routed 2+1 fan manifold."""

from .parameters import RoutingCouponParameters, load_routing_parameters
from .coupons import (
    build_linkage_coupon,
    build_shaft_clearance_coupon,
    build_seal_gap_coupon,
)
from .interfaces import build_p12_fan_pod, build_core_routing_adapter

__all__ = [
    "RoutingCouponParameters",
    "load_routing_parameters",
    "build_linkage_coupon",
    "build_shaft_clearance_coupon",
    "build_seal_gap_coupon",
    "build_p12_fan_pod",
    "build_core_routing_adapter",
]
