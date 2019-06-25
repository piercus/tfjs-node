##
# @license
# Copyright 2018 Google Inc. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

# Node.js TensorFlow Binding config:
{
  'variables' : {
    'tensorflow_include_dir' : '<(module_root_dir)/deps/include',
    'tensorflow_headers' : [
      '<@(tensorflow_include_dir)/tensorflow/c/c_api.h',
      '<@(tensorflow_include_dir)/tensorflow/c/eager/c_api.h',
    ],
    'tensorflow-library-action': 'move'
  },
  'targets' : [{
    'target_name' : 'tfjs_binding',
    'sources' : [
      'binding/tfjs_backend.cc',
      'binding/tfjs_binding.cc'
    ],
    'include_dirs' : [ '..', '<(tensorflow_include_dir)' ],
    'conditions' : [
      [
        'OS=="linux"', {
          'libraries' : [
            '-Wl,-rpath,\$$ORIGIN/../../deps/lib',
            '-ltensorflow',
            '-ltensorflow_framework',
          ],
          'library_dirs' : ['<(module_path)'],
          'actions': [
            {
              'action_name': 'deps-stage',
              'inputs': [
                '<(module_root_dir)/scripts/deps-stage.js'
              ],
              'outputs': [
                '<(module_path)/libtensorflow.so',
              ],
              'action': [
                'node',
                '<@(_inputs)',
                '<@(tensorflow-library-action)',
                '<(module_path)'
              ]
            }
          ],
        }
      ],
      [
        'OS=="mac"', {
          'libraries' : [
            '<(module_root_dir)/deps/lib/libtensorflow.dylib',
            '<(module_root_dir)/deps/lib/libtensorflow_framework.dylib',
          ],
          'postbuilds': [
            {
              'postbuild_name': 'Adjust libtensorflow load path',
              'action': [
                'install_name_tool',
                "-change",
                "@rpath/libtensorflow.1.dylib",
                "@loader_path/../../deps/lib/libtensorflow.dylib",
                "<@(PRODUCT_DIR)/tfjs_binding.node"
              ]
            },
            {
              'postbuild_name': 'Adjust libtensorflow_framework load path',
              'action': [
                'install_name_tool',
                "-change",
                "@rpath/libtensorflow_framework.1.dylib",
                "@loader_path/../../deps/lib/libtensorflow_framework.dylib",
                "<@(PRODUCT_DIR)/tfjs_binding.node"
              ]
            }，
            {
              'action_name': 'deps-stage',
              'inputs': [
                '<(module_root_dir)/scripts/deps-stage.js'
              ],
              'outputs': [
                '<(module_path)/libtensorflow.dylib',
              ],
               'action': [
                'node',
                '<@(_inputs)',
                '<@(tensorflow-library-action)',
                '<(module_path)'
              ]
            }
          ],
        }
      ],
      [
        'OS=="win"', {
          'defines': ['COMPILER_MSVC'],
          'libraries': ['tensorflow'],
          'library_dirs' : ['<(module_path)'],
          'variables': {
            'tensorflow-library-target': 'windows'
          },
          'msvs_disabled_warnings': [
            # Warning	C4190: 'TF_NewWhile' has C-linkage specified, but returns
            # UDT 'TF_WhileParams' which is incompatible with C.
            # (in include/tensorflow/c/c_api.h)
            4190
          ],
          'actions': [
            {
              'action_name': 'deps-stage',
              'inputs': [
                '<(module_root_dir)/scripts/deps-stage.js'
              ],
              'outputs': [
                '<(module_path)/tensorflow.dll',
              ],
              'action': [
                'node',
                '<@(_inputs)',
                '<@(tensorflow-library-action)',
                '<(module_path)'
              ]
            },
            {
              'action_name': 'generate_def',
              'inputs': [
                '<(module_root_dir)/scripts/generate_defs.js',
                '<@(tensorflow_headers)',
                "<(module_path)/tensorflow.dll"
              ],
              'outputs': [
                '<(module_path)/tensorflow.def'
              ],
              'action': [
                'cmd',
                '/c node --max-old-space-size=4096 <@(_inputs) > <@(_outputs)'
              ]
            },
            {
              'action_name': 'build-tensorflow-lib',
              'inputs': [
                '<(module_path)/tensorflow.def'
              ],
              'outputs': [
                '<(module_path)/tensorflow.lib'
              ],
              'action': [
                'lib',
                '/def:<@(_inputs)',
                '/out:<@(_outputs)',
                '/machine:<@(target_arch)'
              ]
            },
          ],
        },
      ]
    ],
  }
  , {
      "target_name": "action_after_build",
      "type": "none",
      "dependencies": [ "<(module_name)" ],
      "copies": [
        {
          "files": [ "<(module_name).node" ],
          "destination": "<(module_path)"
          # "destination": "<(PRODUCT_DIR)"
        }
      ]
    }
    ],
  "defines": [
      "NAPI_VERSION=<(napi_build_version)"
  ]
}
