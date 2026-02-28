def unwrap_results(res):
    return (
        res.data["results"]
        if isinstance(res.data, dict) and "results" in res.data
        else res.data
    )
