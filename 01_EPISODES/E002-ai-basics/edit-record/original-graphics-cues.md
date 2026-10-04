# Episode 1 v6: on-screen clarification cues

Four short, static OOOD brand pop-ups in both current review videos. Card assets use Teachers, blue/cream/foam/navy and an internal waterline. Each card sits over the lower torso, above typical subtitle placement; sampled composites show no covered face. No chapter cards or additional graphics appear within the conversation. The theme version separately adds its title and outro cards.

| Output time | Raw cue | Copy | Purpose/source | Asset |
|---|---|---|---|---|
| 00:02:02.900–00:02:08.400 | 00:02:17.900 | The flagship models here are closed. OpenAI also offers open-weight gpt-oss. | [Primary source](https://help.openai.com/en/articles/11870455-openai-open-weight-models) | `graphics/v6-model-access-cropped.png` |
| 00:27:41.567–00:27:45.567 | 00:29:02.533 | A GPU is a chip. | [Primary source](https://www.nvidia.com/en-us/geforce/news/introduction-to-pc-components/) | `graphics/v6-gpu-chip-cropped.png` |
| 00:28:25.067–00:28:28.567 | 00:29:46.033 | *Graphics processing unit | [Primary source](https://docs.nvidia.com/cuda/cuda-programming-guide/01-introduction/introduction.html) | `graphics/v6-gpu-name-cropped.png` |
| 00:44:21.600–00:44:27.100 | 00:46:38.400 | Its nonprofit still controls its for-profit arm. | [Primary source](https://openai.com/our-structure/) | `graphics/v6-openai-structure-cropped.png` |

The source popup artwork and its editable JSON are alongside each cropped render asset under `graphics/`. Cropping retains only the 1221×251 card rectangle, placed at output x=96, y=615; this produces the same visual as shifting the original 1920×1080 transparent canvas upward by 90 px while making rendering efficient. Static cards have hard on/off timing; motion was not requested. Sampled source-frame composites and final-export popup frames are retained under `intermediate/` for visual QA.
