def process_request(self, request):
    if not self.cerber.check(request):
        return {"error": "blocked by Cerber"}
    return {"response": f"ALFA processed: {request}"}

def check(self, request):
    # prosta symulacja – później wstawimy Twój kod z repo
    if "hack" in request.lower():
        return False
    return True