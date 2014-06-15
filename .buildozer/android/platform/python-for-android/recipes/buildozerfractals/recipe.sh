#!/bin/bash

VERSION_buildozerfractals=0.1
DEPS_buildozerfractals=(android)
MD5_buildozerfractals=
BUILD_buildozerfractals=/srv/home/droundy/src/visual-hash
RECIPE_buildozerfractals=$RECIPES_PATH/buildozerfractals

function prebuild_buildozerfractals() {
	true
}

function shouldbuild_buildozerfractals() {
	if [ -d "$SITEPACKAGES_PATH/buildozerfractals" ]; then
		DO_BUILD=0
	fi
}

function build_buildozerfractals() {
	cd $BUILD_buildozerfractals

	push_arm

	export LDFLAGS="$LDFLAGS -L$LIBS_PATH"
	export LDSHARED="$LIBLINK"

	# fake try to be able to cythonize generated files
  cython $BUILD_buildozerfractals/VisualHashPrivate/OptimizedFractalTransform.pyx
	$HOSTPYTHON setup.py build_ext --inplace
	try $HOSTPYTHON setup.py install -O2

	unset LDSHARED
	pop_arm
}

function postbuild_buildozerfractals() {
	true
}
