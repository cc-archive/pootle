%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           virtaal
Version:        0.1
Release:        1%{?dist}
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


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --install-data=/usr/share --root $RPM_BUILD_ROOT
mv $RPM_BUILD_ROOT/usr/share/%{name}/data/virtaal.glade $RPM_BUILD_ROOT/usr/share/%{name}
rmdir $RPM_BUILD_ROOT/usr/share/%{name}/data
desktop-file-install --vendor="fedora" --dir=%{buildroot}%{_datadir}/applications virtaal.desktop


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
# Need macro that creates all the translations
%doc README
%{_bindir}/*
%{_datadir}/*
%{python_sitelib}/virtaal*
%{python_sitelib}/*egg-info
%exclude %{_bindir}/*.pyc
%exclude %{_bindir}/*.pyo


%changelog
* Sat Apr 5 2008 Dwayne Bailey <dwayne@translate.org.za> - 0.1-1.fc8
- Initial packaging
