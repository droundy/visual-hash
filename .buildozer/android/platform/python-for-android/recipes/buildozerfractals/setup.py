bfrom distutils.core import setup
from distutils.extension import Extension

setup(
    name='buildozerfractals',
    ext_modules = [Extension("VisualHashPrivate.OptimizedFractalTransform",
                             ["VisualHashPrivate/OptimizedFractalTransform.c"],
                             extra_compile_args=['-std=c99'] )]
)
