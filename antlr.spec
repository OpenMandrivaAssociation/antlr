%global debug_package %{nil}
# since we have only a static library

Summary:		ANother Tool for Language Recognition
Name:			antlr
Version:		2.7.7
Release:		20
License:		Public Domain
URL:			http://www.antlr.org/
Group:			Development/Java
Source0:		http://www.antlr2.org/download/antlr-%{version}.tar.gz
Source1:		%{name}-build.xml
Source2:		%{name}-script
Patch1:			%{name}-%{version}-newgcc.patch

%ifarch %ix86 x86_64 ia64 armv4l sparcv9 alpha s390x ppc ppc64
BuildRequires:	mono
BuildRequires:	mono-winforms
%endif
BuildRequires:	ant
BuildRequires:	java-javadoc
BuildRequires:	jpackage-utils
BuildRequires:	java-1.6.0-openjdk-devel

Requires:		jpackage-utils
Requires:		java

%description
ANTLR, ANother Tool for Language Recognition, (formerly PCCTS) is a
language tool that provides a framework for constructing recognizers,
compilers, and translators from grammatical descriptions containing
C++ or Java actions [You can use PCCTS 1.xx to generate C-based
parsers].

%package			tool
Group:				Development/Java
Summary:			ANother Tool for Language Recognition
BuildArch:			noarch
Requires:			jpackage-utils
Requires:			java
%rename		%{name}

%description	tool
ANTLR, ANother Tool for Language Recognition, (formerly PCCTS) is a
language tool that provides a framework for constructing recognizers,
compilers, and translators from grammatical descriptions containing
C++ or Java actions [You can use PCCTS 1.xx to generate C-based
parsers].

%package		manual
Group:			Development/Java
Summary:		Manual for %{name}
BuildArch:		noarch

%description	manual
Documentation for %{name}.

%package		javadoc
Group:			Development/Java
Summary:		Javadoc for %{name}
BuildArch:		noarch

%description	javadoc
Javadoc for %{name}.

%package		C++
Group:			Development/Java
Summary:		C++ bindings for antlr2 generated parsers
Provides:		antlr-static = %{version}-%{release}
%rename		%{name}-native

%description	C++
This package provides a static C++ library for parsers generated by ANTLR2.

%package		C++-doc
Group:			Development/Java
Summary:		Documentation for C++ bindings for antlr2 generated parsers
BuildRequires:	doxygen
BuildArch:		noarch

%description	C++-doc
This package contains the documentation for the C++ bindings for parsers
generated by ANTLR2.

%package		python
Group:			Development/Java
Summary:		Python runtime support for ANTLR-generated parsers
BuildRequires:	python-devel
BuildRequires:	python-setuptools
BuildArch:		noarch

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
rm -rf %{buildroot}
mkdir -p %{buildroot}{%{_includedir}/%{name},%{_libdir},%{_bindir}}

# jars
mkdir -p %{buildroot}%{_javadir}
cp -p work/lib/%{name}.jar %{buildroot}%{_javadir}/%{name}-%{version}.jar
(cd %{buildroot}%{_javadir} && for jar in *-%{version}.jar; do ln -sf ${jar} `echo $jar| sed "s|-%{version}||g"`; done)

# script
install -p -m 755 %{SOURCE2} %{buildroot}%{_bindir}/antlr

# C++ lib and headers, antlr-config

install -p -m 644 lib/cpp/antlr/*.hpp %{buildroot}%{_includedir}/%{name}
install -p -m 644 lib/cpp/src/libantlr.a %{buildroot}%{_libdir}
install -p -m 755 scripts/antlr-config %{buildroot}%{_bindir}

# javadoc
mkdir -p %{buildroot}%{_javadocdir}/%{name}-%{version}
cp -pr work/api/* %{buildroot}%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}

# python
cd lib/python
%{__python} setup.py install -O1 --skip-build --root %{buildroot}
cd ../..


%files tool
%doc LICENSE.txt
%{_javadir}/%{name}*.jar
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
%doc %{_javadocdir}/%{name}-%{version}
%doc %{_javadocdir}/%{name}

%files python
%{python_sitelib}/antlr/*
%{python_sitelib}/antlr-*


%changelog
* Tue Jan 03 2012 Paulo Andrade <pcpa@mandriva.com.br> 2.7.7-19
+ Revision: 748751
- clean defattr, BR and clean section (patch by zemo)
- add rename entries to fix upgrade (patch by zemo)

* Sun Nov 27 2011 Guilherme Moro <guilherme@mandriva.com> 2.7.7-18
+ Revision: 733789
- rebuild
- imported package antlr

  + Paulo Andrade <pcpa@mandriva.com.br>
    - Use previous package names and provide newer ones
    - Rebuild

* Mon May 02 2011 Oden Eriksson <oeriksson@mandriva.com> 0:2.7.7-12
+ Revision: 662767
- mass rebuild

  + Funda Wang <fwang@mandriva.org>
    - we do not require alternatives for native

* Sun Oct 17 2010 Funda Wang <fwang@mandriva.org> 0:2.7.7-11mdv2011.0
+ Revision: 586334
- requires jre

* Sun Oct 17 2010 Funda Wang <fwang@mandriva.org> 0:2.7.7-10mdv2011.0
+ Revision: 586286
- antlr-native shouldnot provide main package

* Sun Oct 17 2010 Funda Wang <fwang@mandriva.org> 0:2.7.7-9mdv2011.0
+ Revision: 586251
- add more requires

* Sun Oct 17 2010 Funda Wang <fwang@mandriva.org> 0:2.7.7-8mdv2011.0
+ Revision: 586215
- fix requires

* Sun Oct 17 2010 Funda Wang <fwang@mandriva.org> 0:2.7.7-7mdv2011.0
+ Revision: 586211
- merge fedora spec so that we could build c++ interface and java interface at one time

* Tue Mar 16 2010 Oden Eriksson <oeriksson@mandriva.com> 0:2.7.7-6mdv2010.1
+ Revision: 521995
- rebuilt for 2010.1

* Sun Aug 09 2009 Oden Eriksson <oeriksson@mandriva.com> 0:2.7.7-5mdv2010.0
+ Revision: 413028
- rebuild

* Fri Mar 06 2009 Antoine Ginies <aginies@mandriva.com> 0:2.7.7-4mdv2009.1
+ Revision: 349989
- 2009.1 rebuild

* Thu Jul 24 2008 Thierry Vignaud <tv@mandriva.org> 0:2.7.7-3mdv2009.0
+ Revision: 245440
- rebuild

* Wed Jan 23 2008 Alexander Kurtakov <akurtakov@mandriva.org> 0:2.7.7-2.3.1mdv2008.1
+ Revision: 157052
- fix build

  + Thierry Vignaud <tv@mandriva.org>
    - BuildRequires  jakarta-commons-launcher
    - rebuild
    - kill re-definition of %%buildroot on Pixel's request
    - kill file require on update-alternatives

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

* Sat Sep 15 2007 Anssi Hannula <anssi@mandriva.org> 0:2.7.7-1.3mdv2008.0
+ Revision: 87196
- rebuild to filter out autorequires of GCJ AOT objects
- remove unnecessary Requires(post) on java-gcj-compat

* Tue Jul 03 2007 Anssi Hannula <anssi@mandriva.org> 0:2.7.7-1.2mdv2008.0
+ Revision: 47573
- rebuild with new libgcj


* Sat Jan 20 2007 David Walluck <walluck@mandriva.org> 2.7.7-1.1mdv2007.0
+ Revision: 111177
- 2.7.7
- Import antlr

* Thu Aug 10 2006 David Walluck <walluck@mandriva.org> 0:2.7.6-4.1mdv2007.0
- add javadoc %%postun

* Fri Aug 04 2006 David Walluck <walluck@mandriva.org> 0:2.7.6-2.2mdv2007.0
- use bcond

* Tue Jul 18 2006 David Walluck <walluck@mandriva.org> 0:2.7.6-2.1mdv2007.0
- bump release for JPackage 1.7

* Mon Jul 17 2006 David Walluck <walluck@mandriva.org> 0:2.7.6-1.3mdv2007.0
- fix bootstrap

* Sun Jun 04 2006 David Walluck <walluck@mandriva.org> 0:2.7.6-1.2mdv2007.0
- rebuild for libgcj.so.7
- aot-compile

* Fri Jan 13 2006 David Walluck <walluck@mandriva.org> 0:2.7.6-1.1mdk
- 2.7.6

* Thu Sep 15 2005 Götz Waschk <waschk@mandriva.org> 2.7.5-1mdk
- update file list
- New release 2.7.5

* Fri May 13 2005 David Walluck <walluck@mandriva.org> 0:2.7.4-2.2mdk
- rebuild as non-bootstrap

* Sun May 08 2005 David Walluck <walluck@mandriva.org> 0:2.7.4-2.1mdk
- release

* Sat Aug 21 2004 Ralph Apel <r.apel at r-apel.de> - 0:2.7.4-2jpp
- Build with ant-1.6.2.
- Made native scripts conditional

* Wed May 19 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:2.7.4-1jpp
- Update to 2.7.4.

* Sat Apr 03 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:2.7.3-2jpp
- Create alternatives also on upgrades.

* Thu Apr 01 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:2.7.3-1jpp
- Update to 2.7.3.
- Include gcj build option and a native subpackage, build using
  "--with native" to get that.
- Add /usr/bin/antlr alternative.

