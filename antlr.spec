%bcond_with bootstrap
%define section free
%define jedit 0
%define native 0
%define gcj_support 1
%if %{native}
%define gcj_support 0
%endif

Summary:        ANother Tool for Language Recognition
Name:           antlr
Version:        2.7.7
Release:        %mkrel 1.3
Epoch:          0
License:        Public Domain
URL:            http://www.antlr.org/
Group:          Development/Java
#Vendor:        JPackage Project
#Distribution:  JPackage
Source0:        http://www.antlr.org/download/antlr-%{version}.tar.gz
Source1:        %{name}-build.xml
Source2:        %{name}-script
Source3:        http://www.antlr.org/share/1069557132934/makefile.gcj
Patch0:         %{name}-jedit.patch

%if %{native}
BuildRequires:  gcc-java, make
%else
%if %{gcj_support}
BuildRequires:  java-gcj-compat-devel
%else
Buildarch:      noarch
%endif
BuildRequires:  ant
BuildRequires:  perl
%if %without bootstrap
BuildRequires:  java-javadoc
%endif
Requires:       jpackage-utils
Requires(post): update-alternatives
Requires(postun): update-alternatives
%endif

%description
ANTLR, ANother Tool for Language Recognition, (formerly PCCTS) is a
language tool that provides a framework for constructing recognizers,
compilers, and translators from grammatical descriptions containing
C++ or Java actions [You can use PCCTS 1.xx to generate C-based
parsers].

%package        native
Group:          Development/Java
Summary:        ANother Tool for Language Recognition (native version)
Provides:       %{name} = %{epoch}:%{version}-%{release}
Requires(post): update-alternatives
Requires(postun): update-alternatives

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

%if %{jedit}
%package        jedit
Group:          Text Editors
Summary:        ANTLR mode for jEdit
Requires:       jedit >= 0:4.1

%description    jedit
ANTLR mode for jEdit.  To enable this mode, insert the following into your
%{_datadir}/jedit/modes/catalog:

  <MODE NAME="antlr" FILE="antlr.xml" FILE_NAME_GLOB="*.g"/>
%endif

%prep
%setup -q
# remove all binary libs
find . -name "*.jar" -exec rm -f {} \;
%if !%{native}
%if %{jedit}
%patch0 -p0
%endif
cp -p %{SOURCE1} build.xml
%endif


%build
%if %{native}
%{__make} -f %{SOURCE3} COMPOPTS="$RPM_OPT_FLAGS"
%else
%if %without bootstrap
%ant -Dj2se.apidoc=%{_javadocdir}/java jar javadoc
%else
%ant -Dj2se.apidoc=%{_javadocdir}/java jar
%endif
%endif


%install
rm -rf $RPM_BUILD_ROOT

install -dm 755 $RPM_BUILD_ROOT%{_bindir}
touch $RPM_BUILD_ROOT%{_bindir}/antlr # for %%ghost

%if %{native}

install -pm 755 cantlr $RPM_BUILD_ROOT%{_bindir}/antlr-native

%else
# jars
mkdir -p $RPM_BUILD_ROOT%{_javadir}
cp -p work/lib/%{name}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}.jar; do ln -sf ${jar} `echo $jar| sed "s|-%{version}||g"`; done)

# script
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{_bindir}/antlr-java

# javadoc
%if %without bootstrap
mkdir -p $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr work/api/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name}
%endif

# jedit mode
%if %{jedit}
mkdir -p $RPM_BUILD_ROOT%{_datadir}/jedit/modes
cp -p extras/antlr-jedit.xml $RPM_BUILD_ROOT%{_datadir}/jedit/modes/antlr.xml
%endif
%endif

%{__perl} -pi -e 's/\r$//g' LICENSE.txt doc/{index.html,python-runtime.html}

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
%if %{gcj_support}
%{update_gcjdb}
%endif
%{_sbindir}/update-alternatives --install %{_bindir}/antlr \
  %{name} %{_bindir}/antlr-java 10

%postun
if [ $1 -eq 0 ] ; then
  %{_sbindir}/update-alternatives --remove %{name} %{_bindir}/antlr-java
fi
%if %{gcj_support}
%{clean_gcjdb}
%endif

%if %{native}
%post native
%{_sbindir}/update-alternatives --install %{_bindir}/antlr \
  %{name} %{_bindir}/antlr-native 20

%postun native
if [ $1 -eq 0 ] ; then
  %{_sbindir}/update-alternatives --remove %{name} %{_bindir}/antlr-native
fi
%endif

%if %without bootstrap
%post javadoc
rm -f %{_javadocdir}/%{name}
ln -s %{name}-%{version} %{_javadocdir}/%{name}

%postun javadoc
if [ $1 -eq 0 ]; then
  %{__rm} -f %{_javadocdir}/%{name}
fi
%endif

%if %{native}
%files native
%defattr(0644,root,root,0755)
%doc LICENSE.txt
%defattr(0755,root,root,0755)
%ghost %{_bindir}/antlr
%{_bindir}/antlr-native

%else
%files
%defattr(0644,root,root,0755)
%doc LICENSE.txt
%{_javadir}/%{name}*.jar
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*
%endif
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

%if %{jedit}
%files jedit
%defattr(0644,root,root,0755)
%{_datadir}/jedit/modes/*
%endif
%endif


