"""Host eligibility and state around the existing Splot Mojo engine."""


class Fusion:
    def __init__(self, profile):
        from splot.api import fuse_json
        self._fuse = fuse_json
        self.profile = str(profile)
        self.state = None
        self.context = None
        self.last_envelope = None

    def choose(self, observations, **frame):
        context = (frame["run_id"], frame["shot_id"], frame["target_id"])
        if context != self.context:
            self.state = None
            self.context = context
        by_channel = {}
        for item in observations:
            if item.channel in by_channel:
                raise ValueError("only one observation per channel per round")
            by_channel[item.channel] = item
        eligible = {key: item for key, item in by_channel.items() if item.eligible(**frame)}
        candidates = [
            {"id": key, "payload": {"available": key in eligible, "uncertainty": item.uncertainty}}
            for key, item in by_channel.items()
        ] or [{"id": "unavailable", "payload": {"available": False, "uncertainty": 1.0}}]
        request = {"profile": self.profile, "candidates": candidates}
        if self.state is not None:
            request["state"] = self.state
        envelope = self._fuse(request)
        self.last_envelope = envelope
        self.state = envelope["state"]
        decision = envelope["decision"]
        if decision.get("status") != "selected":
            return None
        return eligible.get(decision.get("selected_candidate_id"))
