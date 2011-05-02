%bcond_with bootstrap

Summary:        ANother Tool for Language Recognition
Name:           antlr
Version:        2.7.7
Release:        %mkrel 12
Epoch:          0
License:        Public Domain
URL:            http://www.antlr.org/
Group:          Development/Java
Source0:        http://www.antlr.org/download/antlr-%{version}.tar.gz
Source1:        %{name}-build.xml
Source2:        %{name}-script
Source3:        http://www.antlr.org/share/1069557132934/makefile.gcj
Patch0:         %{name}-jedit.patch
Patch1:		antlr-2.7.7-newgcc.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires:	mono-winforms
BuildRequires:	ant
BuildRequires:	java-javadoc
BuildRequires:	jpackage-utils
BuildRequires:	java-devel
%if %without bootstrap
BuildRequires:  java-javadoc
%endif
Requires:	jpackage-utils
Requires:	jre
Requires(post): update-alternatives
Requires(postun): update-alternatives

%description
ANTLR, ANother Tool for Language Recognition, (formerly PCCTS) is a
language tool that provides a framework for constructing recognizers,
compilers, and translators from grammatical descriptions containing
C++ or Java actions [You can use PCCTS 1.xx to generate C-based
parsers].

%package        native
Group:          Development/Java
Summary:        ANother Tool for Language Recognition (native version)

%description    native
ANTLR, ANother Tool for Language Recognition, (formerly PCCTS) is a
language tool that provides a framework for constructing recognizers,
compilers, and translators from grammatical descriptions containing
C++ or Java actions [You can use PCCTS 1.xx to generate C-based
parsers].  This package includes the native version of the antlr tool.

%package        manual
Group:          Development/Java
Summary:        Manual for %{name}

%description    manual
Documentation for %{name}.

%if %without bootstrap
%package        javadoc
Group:          Development/Java
Summary:        Javadoc for %{name}

%description    javadoc
Javadoc for %{name}.
%endif

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
%configure2_5x --without-examples
make CXXFLAGS="${CXXFLAGS} -fPIC" DEBUG=1 verbose=1
rm antlr.jar			 # no longer needed

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT{%{_includedir}/%{name},%{_libdir},%{_bindir}}

touch $RPM_BUILD_ROOT%{_bindir}/antlr

# jars
mkdir -p $RPM_BUILD_ROOT%{_javadir}
cp -p work/lib/%{name}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}.jar; do ln -sf ${jar} `echo $jar| sed "s|-%{version}||g"`; done)

# script
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{_bindir}/antlr-java

# C++ lib and headers, antlr-config

install -p -m 644 lib/cpp/antlr/*.hpp $RPM_BUILD_ROOT%{_includedir}/%{name}
install -p -m 644 lib/cpp/src/libantlr.a $RPM_BUILD_ROOT%{_libdir}
install -p -m 755 scripts/antlr-config $RPM_BUILD_ROOT%{_bindir}

# javadoc
%if %without bootstrap
mkdir -p $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr work/api/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name}
%endif

%clean
rm -rf $RPM_BUILD_ROOT

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
