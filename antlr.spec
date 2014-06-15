%{?_javapackages_macros:%_javapackages_macros}
%global debug_package %{nil}
# since we have only a static library

Summary:	ANother Tool for Language Recognition
Name:		antlr
Version:	2.7.7
Release:	32%{?dist}
Epoch:		0
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

%ifarch %ix86 x86_64 ia64 armv4l sparcv9 alpha s390x ppc ppc64
%if ! 0%{?rhel} >= 6
BuildRequires:	mono-core
BuildRequires:	mono-winforms
%endif
%endif
BuildRequires:	ant
BuildRequires:	java-javadoc
BuildRequires:	jpackage-utils
BuildRequires:	java-devel >= 1:1.7.0

Requires:	jpackage-utils
Requires:	java-headless >= 1:1.7.0

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
Requires:	java-headless >= 1:1.7.0
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

%package	C++
Group:		Development/C++
Summary:	C++ bindings for antlr2 generated parsers
Provides:	antlr-static = %{version}-%{release}

%description	C++
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

# this is actually a development package for the C++ target
# as we ship only a static library, it doesn't make sense
# to have a separate -devel package for the headers
%files C++
%{_includedir}/%{name}
%{_libdir}/libantlr.a
%{_bindir}/antlr-config

%files C++-doc
%doc lib/cpp/gen_doc/html/

%files manual
%doc doc/*

%files javadoc
%doc %{_javadocdir}/%{name}

%files python
%{python_sitelib}/antlr/*
%{python_sitelib}/antlr-*
