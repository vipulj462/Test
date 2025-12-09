jobs_db = {}

def create_job(reference_id: str, data: dict):
    jobs_db[reference_id] = data

def update_job(reference_id: str, patch: dict):
   if reference_id not in jobs_db:
      raise KeyError("job not found")
   jobs_db[reference_id].update(patch)