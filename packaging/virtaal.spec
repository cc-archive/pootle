%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           virtaal
Version:        0.1
Release:        5%{?dist}
Summary:        Localization and translation editor

Group:          Development/Tools
License:        GPLv2+
URL:            http://translate.sourceforge.net/wiki/virtaal/index
Source0:        http://downloads.sourceforge.net/translate/%{name}-%{version}.tar.bz2
#Source0:        http://translate.sourceforge.net/snapshots/%{name}-%{version}rc4/%{name}-%{version}rc4.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Patch0:         virtaal-glade-location.patch

BuildArch:      noarch
BuildRequires:  python-devel
BuildRequires:  desktop-file-utils
BuildRequires:  gettext
BuildRequires:  intltool
Requires:       translate-toolkit
Requires:       pygtk2
Requires:       gnome-python2-gtkspell


%description
A Computer Aided Translation (CAT) tool built on the Translate Toolkit.

It includes features that allow a localizer to work effecively including:
syntax highlighting, Translation Memory and glossaries.  Showing only 
the data that is needed.  A simple and effective user interface ensures 
that you can focus on the translation task straight away.

By building on the Translate Toolkit VirTaal is able to edit any of the
following formats: XLIFF, Gettext PO and .mo, Qt .qm, Wordfast TM, TMX,
TBX.  By using the Translate Toolkit converters a translator can edit:
OpenOffice.org SDF, Java (and Mozilla) .properties, Qt .ts and Mozilla DTD.
 

%prep
%setup -q -n %{name}-%{version}
%patch0 -p2 -b .glade

%build
%{__python} setup.py build
./maketranslations
pushd po
for po in $(ls *.po)
do
    mkdir -p locale/$(basename $po .po)/LC_MESSAGES/
    msgfmt $po --output-file=locale/$(basename $po .po)/LC_MESSAGES/%{name}.mo
done
popd


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --install-data=/usr/share --root $RPM_BUILD_ROOT
mv %{buildroot}%{_bindir}/run_virtaal.py %{buildroot}%{_bindir}/virtaal
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
%{_datadir}/virtaal
%{_datadir}/icons
%{python_sitelib}/virtaal*
%{python_sitelib}/*egg-info


%changelog
* Thu Apr 17 2008 Dwayne Bailey <dwayne@translate.org.za> - 0.1-5.fc8
- Install icon

* Thu Apr 17 2008 Dwayne Bailey <dwayne@translate.org.za> - 0.1-4.fc8
- Build translatable files using intltool

* Mon Apr 14 2008 Dwayne Bailey <dwayne@translate.org.za> - 0.1-3.fc8
- Install translations

* Sat Apr 12 2008 Dwayne Bailey <dwayne@translate.org.za> - 0.1-2.fc8
- Executable s/run_virtaal.py/virtaal/
- Remove .glade movement, ./setup.py install it correctly now
- Install .desktop, locale, mime files
- Update desktop- and mime-database

* Sat Apr 5 2008 Dwayne Bailey <dwayne@translate.org.za> - 0.1-1.fc8
- Initial packaging
