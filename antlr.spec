%{?_javapackages_macros:%_javapackages_macros}

%define libname %mklibname antlr 0
%define devname %mklibname -d antlr
%define staticname %mklibname -d -s antlr

Summary:	ANother Tool for Language Recognition
Name:		antlr
Version:	2.7.7
Release:	36
License:	Public Domain
URL:		http://www.antlr.org/
Group:		Development/Java
Source0:	http://www.antlr2.org/download/antlr-%{version}.tar.gz
Source1:	%{name}-build.xml
Source2:	%{name}-script
Source3:	http://repo2.maven.org/maven2/%{name}/%{name}/%{version}/%{name}-%{version}.pom
Source100:	%{name}.rpmlintrc
Patch1:		%{name}-%{version}-newgcc.patch
# see BZ#848662
Patch2:		antlr-examples-license.patch

BuildRequires:	mono
BuildRequires:	mono-winforms
BuildRequires:	ant
BuildRequires:	java-javadoc
BuildRequires:	jpackage-utils javapackages-tools javapackages-local >= 5.3.0
BuildRequires:	java-devel >= 1.8.0

Requires:	jpackage-utils
Requires:	java-headless >= 1.8.0

%description
ANTLR, ANother Tool for Language Recognition, (formerly PCCTS) is a
language tool that provides a framework for constructing recognizers,
compilers, and translators from grammatical descriptions containing
C++ or Java actions [You can use PCCTS 1.xx to generate C-based
parsers].

%package	tool
Group:		Development/Java
Summary:	ANother Tool for Language Recognition
%rename		%{name}
Requires:	jpackage-utils
Requires:	java-headless >= 1.8.0
BuildArch:	noarch

%description	tool
ANTLR, ANother Tool for Language Recognition, (formerly PCCTS) is a
language tool that provides a framework for constructing recognizers,
compilers, and translators from grammatical descriptions containing
C++ or Java actions [You can use PCCTS 1.xx to generate C-based
parsers].

%package	manual
Group:		Development/Java
Summary:	Manual for %{name}
BuildArch:	noarch

%description	manual
Documentation for %{name}.

%package	javadoc
Group:		Development/Java
Summary:	Javadoc for %{name}
BuildArch:	noarch

%description	javadoc
Javadoc for %{name}.

%package -n	%{libname}
Summary:	The antlr2 shared library
Group:		System/Libraries

%description -n	%{libname}
The antlr2 shared library

%package -n	%{devname}
Group:		Development/C++
Summary:	Development files for C++ bindings for antlr2 generated parsers
Requires:	%{libname} = %{EVRD}
%rename %{name}-C++

%description -n	%{devname}
This package provides headers for the C++ library for parsers
generated by ANTLR2.

%package -n	%{staticname}
Group:		Development/C++
Summary:	Static library for C++ bindings for antlr2 generated parsers
Requires:	%{devname} = %{EVRD}
%rename %{name}-static

%description -n	%{staticname}
This package provides a static C++ library for parsers generated by ANTLR2.

%package	C++-doc
Group:		Development/C++
Summary:	Documentation for C++ bindings for antlr2 generated parsers
BuildRequires:	doxygen
BuildArch:	noarch

%description	C++-doc
This package contains the documentation for the C++ bindings for parsers
generated by ANTLR2.

%package	python
Group:		Development/Python
Summary:	Python runtime support for ANTLR-generated parsers
BuildRequires:	pkgconfig(python2)
BuildRequires:	pythonegg(setuptools)
BuildArch:	noarch

%description	python
Python runtime support for ANTLR-generated parsers

%prep
%setup -q
# remove all binary libs
find . -name "*.jar" -exec rm -f {} \;
# Adapt py2 bits
find . -name "*.py" |xargs 2to3 -w
cp -p %{SOURCE1} build.xml
%patch1
%patch2 -p1
# CRLF->LF
sed -i 's/\r//' LICENSE.txt

%build
ant -Dj2se.apidoc=%{_javadocdir}/java
cp work/lib/antlr.jar .  # make expects to find it here
export CLASSPATH=.
%configure --without-examples
make CXXFLAGS="${CXXFLAGS} -fPIC" DEBUG=1 verbose=1
rm antlr.jar			 # no longer needed

# fix doc permissions and remove Makefiles
rm doc/{Makefile,Makefile.in}
chmod 0644 doc/*

# generate doxygen docs for C++ bindings
pushd lib/cpp
	doxygen doxygen.cfg
	find gen_doc -type f -exec chmod 0644 {} \;
popd

# There's no reason whatsoever (outside of broken Makefiles)
# to not build a shared library here...
cd lib/cpp/src
%{__cxx} %{ldflags} -shared -Wl,-soname,libantlr.so.0 -o libantlr.so.0 *.o
# And while at it, LTO in a static library isn't a good idea
# because it breaks other compilers and compiler versions...
for i in *.o; do
	rm -f $i
	%{__cxx} %{optflags} -I.. -fno-lto -o $i -c ${i/.o/.cpp}
done
rm -f libantlr.a
ar cru libantlr.a *.o
ranlib libantlr.a
cd ../../..

# build python
cd lib/python
%{__python} setup.py build
cd ../../

%install
mkdir -p $RPM_BUILD_ROOT{%{_includedir}/%{name},%{_libdir},%{_bindir}}

# jars
mkdir -p $RPM_BUILD_ROOT%{_javadir}
cp -p work/lib/%{name}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}.jar

# script
install -p -m 755 %{SOURCE2} $RPM_BUILD_ROOT%{_bindir}/antlr

# C++ lib and headers, antlr-config

install -p -m 644 lib/cpp/antlr/*.hpp $RPM_BUILD_ROOT%{_includedir}/%{name}
install -p -m 644 lib/cpp/src/libantlr.a $RPM_BUILD_ROOT%{_libdir}
install -p -m 755 lib/cpp/src/libantlr.so.0 $RPM_BUILD_ROOT%{_libdir}
ln -s libantlr.so.0 $RPM_BUILD_ROOT%{_libdir}/libantlr.so
install -p -m 755 scripts/antlr-config $RPM_BUILD_ROOT%{_bindir}

# javadoc
mkdir -p $RPM_BUILD_ROOT%{_javadocdir}/%{name}
cp -pr work/api/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}

# python
cd lib/python
%{__python} setup.py install -O1 --skip-build --root %{buildroot}
cd ../..

# POM and depmap
install -d -m 755 $RPM_BUILD_ROOT%{_mavenpomdir}
install -p -m 644 %{SOURCE3} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP-%{name}.pom
%add_maven_depmap -a antlr:antlrall

%files tool -f .mfiles
%{_bindir}/antlr

%files -n %{libname}
%{_libdir}/libantlr.so.0

%files -n %{devname}
%{_includedir}/%{name}
%{_libdir}/libantlr.so
%{_bindir}/antlr-config

%files -n %{staticname}
%{_libdir}/libantlr.a

%files C++-doc
%doc lib/cpp/gen_doc/html/

%files manual
%doc doc/*

%files javadoc
%doc %{_javadocdir}/%{name}

%files python
%{python_sitelib}/antlr/*
%{python_sitelib}/antlr-*
