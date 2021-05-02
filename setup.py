import os
import sys
import argparse
from shutil import copyfile, copytree, rmtree
from urllib import request
from zipfile import ZipFile
from pathlib import Path

GODOT_PATH = "/home/greg/workspace/repos/godot-git/godot"
OPTIONS = dict(platform='linuxbsd', tools='yes', target='release_debug', bits=64, module_mono_enabled='yes', use_llvm='yes', use_lld='yes')

def download_unpack(rewrite=False):
        # url = 'https://download.pytorch.org/libtorch/cu102/libtorch-cxx11-abi-shared-with-deps-1.7.0.zip'
        url = 'https://download.pytorch.org/libtorch/cpu/libtorch-cxx11-abi-shared-with-deps-1.7.0%2Bcpu.zip'
        if (not Path('libtorch.zip').exists()) or rewrite:
                print('Downloading libtorch')
                filedata = request.urlopen(url)
                datatowrite = filedata.read()
                with open('libtorch.zip', 'wb') as f:
                        f.write(datatowrite)

        if (not Path('GodotModule/libtorch').exists()) or rewrite:
                print('Extracting libtorch')
                with ZipFile('libtorch.zip', 'r') as zipObj:
                        zipObj.extractall(path='GodotModule')
        

def compile_godot(godot_root, **kwargs):
        OPTIONS.update(**kwargs)
        current_path = os.getcwd()
        os.chdir(godot_root)
        arguments = " ".join([f"{k}={i}" for k, i in OPTIONS.items()])
        command = f"scons -j$(nproc) {arguments}"
        print(command)
        assert not os.system(command), "Failed to compile!"
        os.chdir(current_path)

def install_module(godot_root, rewrite=False):
        module_dir = os.path.join(godot_root, 'modules/GodotSharedMemory')
        if (not os.path.exists(module_dir)):
                copytree('GodotModule', module_dir)
        elif rewrite:
                rmtree(module_dir)
                copytree('GodotModule', module_dir)
        
def install_python_module():
        current_path = os.getcwd()
        os.chdir('PythonModule')
        os.system('python3 -m pip install -e .')
        os.chdir(current_path)

def make_glue():
        import glob
        current_path = os.getcwd()
        os.chdir(GODOT_PATH)
        godot_exec = glob.glob(f'./bin/godot.{OPTIONS["platform"]}.*.{OPTIONS["bits"]}.*.mono')
        assert len(godot_exec) == 1, print(godot_exec)
        godot_exec = godot_exec[0]
        os.system(f'{godot_exec} --generate-mono-glue modules/mono/glue')
        os.chdir(current_path)
    

if __name__=='__main__':
        download_unpack(rewrite=False)
        install_module(godot_root=GODOT_PATH, rewrite=True)
        install_python_module()
        # build compile mono
        compile_godot(godot_root=GODOT_PATH, mono_glue='no')
        make_glue()
        compile_godot(godot_root=GODOT_PATH, mono_glue='yes')
        compile_godot(godot_root=GODOT_PATH, tools='no')
        compile_godot(godot_root=GODOT_PATH, platform='server')
