load("@3rdparty_python_pure//:requirements.bzl", "requirement")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "redis",
    srcs = glob([
        "**/*.py",
        "*.py",
    ]),
    deps = [requirement("redis")],
)
