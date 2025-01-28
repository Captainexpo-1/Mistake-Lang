import subprocess
from typing import List, Tuple
from mistake.runtime.runtime_types import MLType, RuntimeListType, BuiltinFunction, RuntimeUnit, Function
import mistake.runtime.stdlib.std_funcs as std
from copy import deepcopy

try:
    import kp
    import numpy as np
except ImportError as e:
    raise ImportError(
        "Mistake GPU support requires additional dependencies. Install them with:\n\n"
        "    pip install mistake-lang[full]\n"
    ) from e


class RuntimeVulkanDevice(MLType):
    def __init__(self):
        pass

    def manager(self):
        return kp.Manager()

    def to_string(self):
        return "VulkanDevice()"

class RuntimeVulkanBuffer(MLType):
    def __init__(self, data: list, dtype: np.dtype):
        self.data = data
        self.dtype = dtype

    def to_string(self):
        return f"VulkanBuffer({self.data}, {repr(self.dtype)})"


def new_vulkan_buffer(arg: RuntimeListType, *_):
    return BuiltinFunction(
        lambda x, *_: RuntimeVulkanBuffer(deepcopy(x).continuous(), arg), imp=False
    )


def actually_run_vulkan_shader(
    threads: Tuple[int, int],
    shader_code: str,
    in_buffers: RuntimeListType,
    out_buffers: RuntimeListType,
    device: RuntimeVulkanDevice,
):
    in_buffs: List[RuntimeVulkanBuffer] = in_buffers.continuous()
    out_buffs: List[RuntimeVulkanBuffer] = out_buffers.continuous()

    def on_finish(result: List[List]):
        for new, cur in zip(result, out_buffs):
            cur.data = [i for i in new]
            
    kompute(threads, shader_code, in_buffs, out_buffs, device, on_finish)

    return RuntimeUnit()    


def run_vulkan_shader(shader_func: Function, *_):
    code = shader_func.body[1:-4]
    code = "".join(i.value for i in code)

    return BuiltinFunction(
        lambda device, *_: BuiltinFunction(
            lambda x_threads, *_: BuiltinFunction(
                lambda y_threads, *_: BuiltinFunction(
                    lambda in_buffers, *_: BuiltinFunction(
                        lambda out_buffers, *_: actually_run_vulkan_shader(
                            (x_threads.value, y_threads.value), code, in_buffers, out_buffers, device
                        ),
                        imp=True,
                    ),
                    imp=False,
                ),
                imp=False,
            ),
            imp=False,
        ),
        imp=False,
    )


def compile_source(shader_code):
    TEMP_DIR = "/tmp"
    # Write the shader code to a temporary file
    with open(f"{TEMP_DIR}/temp_shader.comp", "w") as f:
        f.write(shader_code)

    # Compile the shader using glslangValidator
    result = subprocess.run(
        [
            "glslangValidator",
            "-V",
            f"{TEMP_DIR}/temp_shader.comp",
            "-o",
            f"{TEMP_DIR}/temp_shader.spv",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Shader compilation failed: {result.stderr}")
    # Read the compiled SPIR-V binary
    with open(f"{TEMP_DIR}/temp_shader.spv", "rb") as f:
        spirv = f.read()
    return spirv


def kompute(
    threads: Tuple[int, int],
    shader,
    raw_in: List[RuntimeVulkanBuffer],
    raw_out: List[RuntimeVulkanBuffer],
    manager: RuntimeVulkanDevice,
    finished_callback=None,
):
    
    # 1. Create Kompute Manager with default settings (device 0, first queue and no extensions)
    mgr = manager.manager()


    # 2. Create and initialise Kompute Tensors through manager
    #print(shader)
    in_tensors = [mgr.tensor_t(np.array([i.value for i in buf.data], dtype=buf.dtype)) for buf in raw_in]
    out_tensors = [
        mgr.tensor_t(np.array([i.value for i in buf.data], dtype=buf.dtype)) for buf in raw_out
    ]

    params = [*in_tensors, *out_tensors]

    # 3. Create algorithm based on shader (supports buffers & push/spec constants)
    workgroup = (int(threads[0]), int(threads[1]), 1)

    # See documentation shader section for compile_source
    spirv = compile_source(shader)

    algo = mgr.algorithm(params, spirv, workgroup)

    # 4. Run operation synchronously using sequence
    (
        mgr.sequence()
        .record(kp.OpTensorSyncDevice(params))
        .record(kp.OpAlgoDispatch(algo))  # Binds default push consts provided
        .eval()
    )  # evaluates only the last recorded op

    # 5. Sync results from the GPU asynchronously
    sq = mgr.sequence()
    sq.eval_async(kp.OpTensorSyncLocal(params))
    sq.eval_await()

    out = [i.data().tolist() for i in out_tensors]

    if finished_callback:
        finished_callback(out)

    return out


if __name__ == "__main__":
    # Define a raw string shader (or use the Kompute tools to compile to SPIRV / C++ header
    # files). This shader shows some of the main components including constants, buffers, etc
    shader = """
        #version 460
    
        layout(local_size_x = 1) in;
        
        layout(set = 0, binding = 0) buffer Data {
            uint data[];
        } buf;
        
        void main() {
            uint idx = gl_GlobalInvocationID.x;
            buf.data[idx] *= 26;
        }
    """

    o = kompute(
        shader,
        [RuntimeVulkanBuffer([1, 2, 3, 4, 5], np.uint32)],
        [],
        RuntimeVulkanDevice(),
    )  # [([125,152,182], np.uint32), ([4,5,6], np.uint32)], [([0,0,0], np.uint32), ([0,0,0], np.uint32)])
    print(o)


vulkan_std_funcs = {
    # VULKAN
    "🔥+32": np.uint32,
    "🔥[!]": BuiltinFunction(lambda *args: new_vulkan_buffer(*args)),
    "🔥🔥": RuntimeVulkanDevice(),
    '🔥🔥()': BuiltinFunction(lambda *args: run_vulkan_shader(*args)),
    '🔥[<]': BuiltinFunction(lambda buffer, *_: RuntimeListType([(std.get_type(i) if not isinstance(i, MLType) else i) for i in buffer.data])),
}