#!/usr/bin/env python3
#
# Copyright 2022 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import platform
import shutil
import subprocess
import sys
from pathlib import Path

# Get the path where this script is located so we can invoke the script from
# any directory and have the paths work correctly.
tests_path = Path(__file__).parent.resolve()

# Get the root path as an absolute path, so all derived paths are absolute.
root_path = tests_path.parent.parent.absolute()

# Windows works with subprocess.run a bit differently.
is_windows = platform.system() == "Windows"

# Get the location of the flatc executable
flatc_exe = Path("flatc.exe" if is_windows else "flatc")

# Find and assert flatc compiler is present.
if root_path in flatc_exe.parents:
    flatc_exe = flatc_exe.relative_to(root_path)
flatc_path = Path(root_path, flatc_exe)
assert flatc_path.exists(), "Cannot find the flatc compiler " + str(flatc_path)

def check_call(args, cwd=tests_path):
    subprocess.check_call(args, cwd=str(cwd), shell=is_windows)

# Execute the flatc compiler with the specified parameters
def flatc(options, schema, prefix=None, include=None, data=None, cwd=tests_path):
    cmd = [str(flatc_path)] + options
    if prefix:
        cmd += ["-o"] + [prefix]
    if include:
        cmd += ["-I"] + [include]
    cmd += [schema] if isinstance(schema, str) else schema
    if data:
        cmd += [data] if isinstance(data, str) else data
    check_call(cmd)

print("Removing node_modules/ directory...")
shutil.rmtree(Path(tests_path, "node_modules"), ignore_errors=True)

check_call(["npm", "install", "--silent"])

print("Invoking flatc...")
flatc(
    options=["--ts", "--reflect-names", "--gen-name-strings", "--gen-mutable", "--gen-object-api"],
    schema="../monster_test.fbs",
    include="../include_test",
)

flatc(
    options=["--gen-object-api", "-b"],
    schema="../monster_test.fbs",
    include="../include_test",
    data="../unicode_test.json",
)

flatc(
    options=["--ts", "--reflect-names", "--gen-name-strings", "--gen-mutable", "--gen-object-api"],
    schema="../union_vector/union_vector.fbs",
    prefix="union_vector",
)

flatc(
    options=["--ts", "--reflect-names", "--gen-name-strings"],
    schema="../optional_scalars.fbs",
)

flatc(
    options=["--ts", "--reflect-names", "--gen-name-strings", "--ts-no-import-ext"],
    schema="../optional_scalars.fbs",
    prefix="no_import_ext",
)

flatc(
    options=["--ts", "--reflect-names", "--gen-name-strings", "--gen-mutable", "--gen-object-api"],
    schema=[
        "typescript_keywords.fbs",
        "test_dir/typescript_include.fbs",
        "test_dir/typescript_transitive_include.fbs",
        "../../reflection/reflection.fbs",
    ],
    include="../../",
)

flatc(
    options=["--ts", "--reflect-names", "--ts-flat-files", "--gen-name-strings", "--gen-object-api"],
    schema="arrays_test_complex/arrays_test_complex.fbs",
    prefix="arrays_test_complex"
)

flatc(
    options=[
        "--ts",
        "--reflect-names",
        "--gen-name-strings",
        "--gen-mutable",
        "--gen-object-api",
        "--ts-flat-files",
    ],
    schema=[
        "typescript_keywords.fbs",
        "test_dir/typescript_include.fbs",
        "test_dir/typescript_transitive_include.fbs",
        "../../reflection/reflection.fbs",
    ],
    include="../../",
)

print("Running TypeScript Compiler...")
check_call(["tsc"])

NODE_CMD = ["node"]

print("Running TypeScript Tests...")
check_call(NODE_CMD + ["JavaScriptTest"])
check_call(NODE_CMD + ["JavaScriptUnionVectorTest"])
check_call(NODE_CMD + ["JavaScriptFlexBuffersTest"])
check_call(NODE_CMD + ["JavaScriptComplexArraysTest"])
check_call(NODE_CMD + ["JavaScriptRequiredStringTest"])
