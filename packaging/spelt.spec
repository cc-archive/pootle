%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           spelt
Version:        0.1rc2
Release:        0.1%{?dist}
Summary:        A tool to classify words from a language database according to their roots.

Group:          Development/Tools
License:        GPLv2+
URL:            http://translate.sourceforge.net/wiki/spelt/index
Source0:        http://downloads.sourceforge.net/translate/%{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python-devel
BuildRequires:  desktop-file-utils
BuildRequires:  gettext
BuildRequires:  intltool
Requires:       translate-toolkit
Requires:       pygtk2
Requires:       lxml
Requires:       xdg-utils


%description
Spelt is used to classify words from a language database according to their roots.

The language database is an XML-based format that is only used by Spelt to classify unclassified words.
 

%prep
%setup -q -n %{name}-%{version}

%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --install-data=/usr --root $RPM_BUILD_ROOT

# Cleanup horrid ./setup.py installs
mv %{buildroot}%{_bindir}/run_spelt.py %{buildroot}%{_bindir}/spelt
pushd  %{buildroot}%{_datadir}
mkdir -p mime/packages applications icons
mv spelt/spelt.{png,ico} icons
mv spelt/splash_logo.png icons
popd

desktop-file-install --vendor="fedora" --delete-original \
   --dir=%{buildroot}%{_datadir}/applications            \
   %{buildroot}%{_datadir}/applications/%{name}.desktop
cp -rp po/locale %{buildroot}%{_datadir}/
%find_lang %{name}


%post
update-desktop-database &> /dev/null || :
update-mime-database %{_datadir}/mime &> /dev/null || :
touch --no-create %{_datadir}/icons/hicolor
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
  %{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi


%postun
update-desktop-database &> /dev/null || :
update-mime-database %{_datadir}/mime &> /dev/null || :
touch --no-create %{_datadir}/icons/hicolor
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
  %{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi


%clean
rm -rf $RPM_BUILD_ROOT


%files -f %{name}.lang
%defattr(-,root,root,-)
%doc README
%{_bindir}/*
%{_datadir}/applications/*
%{_datadir}/mime/packages/*
%exclude %{_datadir}/spelt/*.in
%{_datadir}/spelt
%{_datadir}/icons/*
%{python_sitelib}/spelt*
%{python_sitelib}/*egg-info


%changelog
* Mon Aug 18 2008 Walter Leibbrandt <walter@translate.org.za> - 0.1rc2-0.1.fc9
- Initial packaging
