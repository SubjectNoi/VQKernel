# from tvm.script import tir as T

@T.prim_func
def main(AT: T.Buffer((16384, 16384), "float32"), B: T.Buffer((16384, 16384), "float32"), C: T.Buffer((16384, 16384), "float32")):
    T.func_attr({"tir.noalias": T.bool(True)})
    # with T.block("root"):
    AT_shared = T.alloc_buffer((16384, 16384), scope="shared")
    AT_shared_local = T.alloc_buffer((16384, 16384), scope="local")
    B_shared = T.alloc_buffer((16384, 16384), scope="shared")
    B_shared_local = T.alloc_buffer((16384, 16384), scope="local")
    C_local = T.alloc_buffer((16384, 16384), scope="local")
    for ax0, ax1 in T.grid(16384, 16384):
        with T.block("B_shared"):
            v0, v1 = T.axis.remap("SS", [ax0, ax1])
            T.reads(B[v0, v1])
            T.writes(B_shared[v0, v1])
            B_shared[v0, v1] = B[v0, v1]
    for ax0, ax1 in T.grid(16384, 16384):
        with T.block("AT_shared"):
            v0, v1 = T.axis.remap("SS", [ax0, ax1])
            T.reads(AT[v0, v1])
            T.writes(AT_shared[v0, v1])
            AT_shared[v0, v1] = AT[v0, v1]
    for ax0, ax1 in T.grid(16384, 16384):
        with T.block("AT_shared_local"):
            v0, v1 = T.axis.remap("SS", [ax0, ax1])
            T.reads(AT_shared[v0, v1])
            T.writes(AT_shared_local[v0, v1])
            AT_shared_local[v0, v1] = AT_shared[v0, v1]
    for ax0, ax1 in T.grid(16384, 16384):
        with T.block("B_shared_local"):
            v0, v1 = T.axis.remap("SS", [ax0, ax1])
            T.reads(B_shared[v0, v1])
            T.writes(B_shared_local[v0, v1])
            B_shared_local[v0, v1] = B_shared[v0, v1]
    for i_0 in T.thread_binding(128, thread="blockIdx.x"):
        for j_0 in T.thread_binding(128, thread="blockIdx.y"):
            for j_1_0 in T.thread_binding(2, thread="vthread.y"):
                for i_1_0 in T.thread_binding(2, thread="vthread.x"):
                    for j_1_1_0 in T.thread_binding(16, thread="threadIdx.y"):
                        for i_1_1_0 in T.thread_binding(16, thread="threadIdx.x"):
                            for i_1_1_1, j_1_1_1, k_0, k_1 in T.grid(4, 4, 1024, 16):
                                with T.block("B"):
                                    vi = T.axis.spatial(16384, i_0 * 128 + i_1_0 * 64 + i_1_1_0 * 4 + i_1_1_1)
                                    vj = T.axis.spatial(16384, j_0 * 128 + j_1_0 * 64 + j_1_1_0 * 4 + j_1_1_1)
                                    vk = T.axis.reduce(16384, k_0 * 16 + k_1)
                                    T.reads(AT_shared_local[vk, vi], B_shared_local[vk, vj])
                                    T.writes(C_local[vi, vj])
                                    with T.init():
                                        C_local[vi, vj] = T.float32(0)
                                    C_local[vi, vj] = C_local[vi, vj] + AT_shared_local[vk, vi] * B_shared_local[vk, vj]
                            for ax0, ax1 in T.grid(4, 4):
                                with T.block("C_local"):
                                    v0 = T.axis.spatial(16384, i_0 * 128 + i_1_0 * 64 + i_1_1_0 * 4 + ax0)
                                    v1 = T.axis.spatial(16384, j_0 * 128 + j_1_0 * 64 + j_1_1_0 * 4 + ax1)
                                    T.reads(C_local[v0, v1])
                                    T.writes(C[v0, v1])
                                    C[v0, v1] = C_local[v0, v1]