class VisionAdapter:
    def describe(self, image_path: str) -> str:
        return f"VisionAdapter placeholder for {image_path}"

class AudioAdapter:
    def transcribe(self, audio_path: str) -> str:
        return f"AudioAdapter placeholder for {audio_path}"

class StructuredDataAdapter:
    def summarise(self, data) -> str:
        return f"StructuredDataAdapter received {type(data).__name__}"
