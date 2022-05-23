from .database import JobView, SetView


class LANJobView(JobView):
    def __init__(self, manifest, lq):
        self.lq = lq
        for attr in ("name", "count", "created"):
            setattr(self, attr, manifest[attr])
        self.remaining = manifest.get("remaining", self.count)
        self.id = manifest["hash_"]
        self.peer = manifest["peer_"]
        self.sets = []
        self.draft = False
        self.acquired = None
        self.sets = [LANSetView(s, self, i, lq) for i, s in enumerate(manifest["sets"])]

    def save(self):
        self.lq.set_job(self.id, self.as_dict())

    def refresh_sets(self):
        for s in self.sets:
            s.remaining = s.count
        self.save()


class LANSetView(SetView):
    def __init__(self, data, job, rank, lq):
        self.lq = lq
        self.job = job
        self.sd = False
        self.rank = rank
        self.id = f"{job.id}_{rank}"
        for attr in ("path", "count"):
            setattr(self, attr, data[attr])
        self.remaining = data.get("remaining", self.count)
        self.material_keys = ",".join(data.get("materials", []))
        self.profile_keys = ",".join(data.get("profiles", []))
        self._resolved = None

    def resolve(self) -> str:
        if self._resolved is None:
            self._resolved = self.lq.resolve_set(self.job.peer, self.job.id, self.path)
        return self._resolved

    def save(self):
        self.job.save()