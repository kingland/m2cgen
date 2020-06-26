import os
import subprocess
import shutil

import m2cgen as m2c
from tests import utils
from tests.e2e.executors import base


class JavaExecutor(base.BaseExecutor):

    def __init__(self, model):
        self.model = model
        self.class_name = "Model"

        java_home = os.environ.get("JAVA_HOME")
        assert java_home, "JAVA_HOME is not specified"
        self._java_bin = os.path.join(java_home, "bin/java")
        self._javac_bin = os.path.join(java_home, "bin/javac")

    def predict(self, X):

        exec_args = [
            self._java_bin, "-cp", self._resource_tmp_dir,
            "Executor", "Model", "score"
        ]
        exec_args.extend(map(str, X))
        return utils.predict_from_commandline(exec_args)

    def prepare(self):
        # Create files generated by exporter in the temp dir.
        code = m2c.export_to_java(self.model, class_name=self.class_name)
        code_file_name = os.path.join(self._resource_tmp_dir,
                                      f"{self.class_name}.java")

        with open(code_file_name, "w") as f:
            f.write(code)

        # Move Executor.java to the same temp dir.
        module_path = os.path.dirname(__file__)
        shutil.copy(os.path.join(module_path, "Executor.java"),
                    self._resource_tmp_dir)

        # Compile all files together.
        exec_args = [
            self._javac_bin,
            code_file_name,
            os.path.join(self._resource_tmp_dir, "Executor.java")]
        subprocess.call(exec_args)
