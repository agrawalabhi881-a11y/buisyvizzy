"""
backend/app/sim/disruptions.py
Disruption Injection Engine & Network Resilience Tracker.
Allows the Admin to inject stochastic black-swan shocks and tracks
network recovery time.
"""

from typing import Dict, List, Optional
from contracts.models import DisruptionType, DisruptionContract


class DisruptionEngine:
    """Manages injection, duration, and effects of disruptions."""

    def __init__(self):
        self.scheduled_disruptions: List[DisruptionContract] = []
        self.active_disruptions: List[DisruptionContract] = []
        self.disruption_history: List[DisruptionContract] = []
        # Recovery tracking: disruption_id -> {'disruption': d, 'end_tick': int, 'recovered_tick': Optional[int]}
        self.recovery_records: Dict[str, dict] = {}

    def schedule_disruption(self, disruption: DisruptionContract):
        """Adds a disruption to be triggered during the simulation."""
        self.scheduled_disruptions.append(disruption)

    def update_disruptions_for_tick(self, tick: int) -> List[DisruptionContract]:
        """
        Advances disruptions state for current tick:
          - Activates scheduled disruptions matching tick.
          - Retires completed disruptions (tick >= start + duration).
        """
        # Activate newly starting disruptions
        still_scheduled = []
        for d in self.scheduled_disruptions:
            if d.start_tick <= tick < d.start_tick + d.duration_ticks:
                self.active_disruptions.append(d)
                self.recovery_records[d.id] = {
                    "disruption": d,
                    "end_tick": d.start_tick + d.duration_ticks,
                    "recovered_tick": None,
                    "recovery_time_ticks": None,
                }
            else:
                still_scheduled.append(d)
        self.scheduled_disruptions = still_scheduled

        # Expire finished disruptions
        currently_active = []
        for d in self.active_disruptions:
            if tick < d.start_tick + d.duration_ticks:
                currently_active.append(d)
            else:
                self.disruption_history.append(d)
        self.active_disruptions = currently_active
        return self.active_disruptions

    def get_demand_spike_multiplier(self, store_id: str, product_id: str) -> float:
        """Returns demand multiplier if a DEMAND_SPIKE is active on this store/product."""
        multiplier = 1.0
        for d in self.active_disruptions:
            if d.disruption_type == DisruptionType.DEMAND_SPIKE:
                if d.target_id in ("ALL", store_id, product_id):
                    multiplier = max(multiplier, d.severity)
        return multiplier

    def get_supplier_delay_factor(self, mfr_id: str = "MFR_01") -> float:
        """Returns supplier delay multiplier if a SUPPLIER_FAILURE is active."""
        factor = 1.0
        for d in self.active_disruptions:
            if d.disruption_type == DisruptionType.SUPPLIER_FAILURE:
                if d.target_id in ("ALL", mfr_id):
                    factor = max(factor, d.severity)
        return factor

    def get_transit_delay_factor(self, origin_id: str, dest_id: str) -> float:
        """Returns transit latency multiplier if a TRANSPORT_DELAY is active."""
        factor = 1.0
        for d in self.active_disruptions:
            if d.disruption_type == DisruptionType.TRANSPORT_DELAY:
                if d.target_id in ("ALL", origin_id, dest_id):
                    factor = max(factor, d.severity)
        return factor

    def is_warehouse_operational(self, warehouse_id: str) -> bool:
        """Returns False if a WAREHOUSE_OUTAGE is active for this warehouse."""
        for d in self.active_disruptions:
            if d.disruption_type == DisruptionType.WAREHOUSE_OUTAGE:
                if d.target_id == warehouse_id:
                    return False
        return True

    def check_recovery(self, tick: int, current_fill_rate: float, recovery_threshold: float = 0.95):
        """
        Monitors post-disruption stabilization:
        When fill rate reaches >= threshold after disruption has finished, marks recovery time.
        """
        for rec in self.recovery_records.values():
            if rec["recovered_tick"] is None and tick >= rec["end_tick"]:
                if current_fill_rate >= recovery_threshold:
                    rec["recovered_tick"] = tick
                    rec["recovery_time_ticks"] = tick - rec["end_tick"]
