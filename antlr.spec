%bcond_with bootstrap

%define		build_mono		0

Summary:	ANother Tool for Language Recognition
Name:		antlr
Version:	2.7.7
Release:	17
License:	Public Domain
URL:		http://www.antlr.org/
Group:		Development/Java
Source0:	http://www.antlr.org/download/antlr-%{version}.tar.gz
Source1:	%{name}-build.xml
Source2:	%{name}-script
Source3:	http://www.antlr.org/share/1069557132934/makefile.gcj
Patch0:		%{name}-jedit.patch
Patch1:		antlr-2.7.7-newgcc.patch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
%ifnarch %arm
%if %{build_mono}
BuildRequires:	mono-winforms
%endif
%endif
BuildRequires:	ant
BuildRequires:	java-devel
BuildRequires:	jpackage-utils
%if %without bootstrap
BuildRequires:	java-javadoc
%endif
Requires:	java
Requires:	jpackage-utils
Requires(post):	update-alternatives
Requires(postun): update-alternatives
Provides:	%{name}-tool = %{EVRD}

%description
ANTLR, ANother Tool for Language Recognition, (formerly PCCTS) is a
language tool that provides a framework for constructing recognizers,
compilers, and translators from grammatical descriptions containing
C++ or Java actions [You can use PCCTS 1.xx to generate C-based
parsers].

%package	native
Group:		Development/Java
Summary:	ANother Tool for Language Recognition (native version)
Provides:	%{name}-C++ = %{EVRD}

%description	native
ANTLR, ANother Tool for Language Recognition, (formerly PCCTS) is a
language tool that provides a framework for constructing recognizers,
compilers, and translators from grammatical descriptions containing
C++ or Java actions [You can use PCCTS 1.xx to generate C-based
parsers].  This package includes the native version of the antlr tool.

%package	manual
Group:		Development/Java
Summary:	Manual for %{name}

%description	manual
Documentation for %{name}.

%if %without bootstrap
%package	javadoc
Group:		Development/Java
Summary:	Javadoc for %{name}

%description	javadoc
Javadoc for %{name}.
%endif

%package	python
Group:		Development/Java
Summary:	Python runtime support for ANTLR-generated parsers
BuildRequires:	python-devel
BuildRequires:	python-setuptools
BuildArch:	noarch

%description	python
Python runtime support for ANTLR-generated parsers

%prep
%setup -q
# remove all binary libs
find . -name "*.jar" -exec rm -f {} \;
cp -p %{SOURCE1} build.xml
%patch1
# CRLF->LF
sed -i 's/\r//' LICENSE.txt

%build
ant -Dj2se.apidoc=%{_javadocdir}/java
cp work/lib/antlr.jar .  # make expects to find it here
export CLASSPATH=.
%configure2_5x --without-examples			\
%if %{build_mono}
	--enable-mono
%else
	--disable-mono
%endif

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
rm -rf %{buildroot}
mkdir -p %{buildroot}{%{_includedir}/%{name},%{_libdir},%{_bindir}}

touch %{buildroot}%{_bindir}/antlr

# jars
mkdir -p %{buildroot}%{_javadir}
cp -p work/lib/%{name}.jar %{buildroot}%{_javadir}/%{name}-%{version}.jar
(cd %{buildroot}%{_javadir} && for jar in *-%{version}.jar; do ln -sf ${jar} `echo $jar| sed "s|-%{version}||g"`; done)

# script
cp -p %{SOURCE2} %{buildroot}%{_bindir}/antlr-java

# C++ lib and headers, antlr-config

install -p -m 644 lib/cpp/antlr/*.hpp %{buildroot}%{_includedir}/%{name}
install -p -m 644 lib/cpp/src/libantlr.a %{buildroot}%{_libdir}
install -p -m 755 scripts/antlr-config %{buildroot}%{_bindir}

# javadoc
%if %without bootstrap
mkdir -p %{buildroot}%{_javadocdir}/%{name}-%{version}
cp -pr work/api/* %{buildroot}%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}
%endif

# python
cd lib/python
%{__python} setup.py install -O1 --skip-build --root %{buildroot}
cd ../..

%clean
rm -rf %{buildroot}

%post
%{_sbindir}/update-alternatives --install %{_bindir}/antlr \
  %{name} %{_bindir}/antlr-java 10

%postun
if [ $1 -eq 0 ] ; then
  %{_sbindir}/update-alternatives --remove %{name} %{_bindir}/antlr-java
fi

%if %without bootstrap
%post javadoc
rm -f %{_javadocdir}/%{name}
ln -s %{name}-%{version} %{_javadocdir}/%{name}

%postun javadoc
if [ $1 -eq 0 ]; then
  %{__rm} -f %{_javadocdir}/%{name}
fi
%endif

%files native
%defattr(0644,root,root,0755)
%defattr(-,root,root,-)
%{_includedir}/%{name}
%{_libdir}/libantlr.a
%{_bindir}/antlr-config

%files
%defattr(0644,root,root,0755)
%doc LICENSE.txt
%{_javadir}/%{name}*.jar
%defattr(0755,root,root,0755)
%ghost %{_bindir}/antlr
%{_bindir}/antlr-java

%files manual
%defattr(0644,root,root,0755)
%doc doc/*

%if %without bootstrap
%files javadoc
%defattr(0644,root,root,0755)
%doc %{_javadocdir}/%{name}-%{version}
%ghost %doc %{_javadocdir}/%{name}
%endif

%files python
%defattr(-,root,root,-)
%{python_sitelib}/antlr/*
%{python_sitelib}/antlr-*
