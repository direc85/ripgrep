Name:       ripgrep
Summary:    Line-oriented search tool similar to The Silver Searcher, ack and grep
Version:    13.0.0
Release:    1
Group:      Application/System
License:    MIT
URL:        https://github.com/direc85/ripgrep
Source0:    %{version}.tar.gz
BuildRequires:  rust >= 1.52.1+git1-1
BuildRequires:  cargo >= 1.52.1+git1-1
BuildRequires:  rust-std-static
BuildRequires:  curl

%description
ripgrep is a line-oriented search tool that recursively searches the current
directory for a regex pattern while respecting gitignore rules. ripgrep has
first class support on Windows, macOS and Linux.

%prep
%setup -q -n %{name}-%{version}

%build

if [ ! -f "%{version}.tar.gz" ]
then
  curl -LO https://github.com/BurntSushi/ripgrep/archive/refs/tags/%{version}.tar.gz
fi

if [ ! -d "%{name}-%{version}" ]
then
  tar xfz %{version}.tar.gz
  sed -i 's/debug = 1/debug = 0\nlto = true/' %{name}-%{version}/Cargo.toml
fi

rustc --version
cargo --version

# https://git.sailfishos.org/mer-core/gecko-dev/blob/master/rpm/xulrunner-qt5.spec#L224
# When cross-compiling under SB2 rust needs to know what arch to emit
# when nothing is specified on the command line. That usually defaults
# to "whatever rust was built as" but in SB2 rust is accelerated and
# would produce x86 so this is how it knows differently. Not needed
# for native x86 builds
%ifarch %arm
export SB2_RUST_TARGET_TRIPLE=armv7-unknown-linux-gnueabihf
export CFLAGS_armv7_unknown_linux_gnueabihf=$CFLAGS
export CXXFLAGS_armv7_unknown_linux_gnueabihf=$CXXFLAGS
%endif
%ifarch aarch64
export SB2_RUST_TARGET_TRIPLE=aarch64-unknown-linux-gnu
export CFLAGS_aarch64_unknown_linux_gnu=$CFLAGS
export CXXFLAGS_aarch64_unknown_linux_gnu=$CXXFLAGS
%endif
%ifarch %ix86
export SB2_RUST_TARGET_TRIPLE=i686-unknown-linux-gnu
export CFLAGS_i686_unknown_linux_gnu=$CFLAGS
export CXXFLAGS_i686_unknown_linux_gnu=$CXXFLAGS
%endif

export CFLAGS="-O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=4 -Wformat -Wformat-security -fmessage-length=0"
export CXXFLAGS=$CFLAGS
# This avoids a malloc hang in sb2 gated calls to execvp/dup2/chdir
# during fork/exec. It has no effect outside sb2 so doesn't hurt
# native builds.
export SB2_RUST_EXECVP_SHIM="/usr/bin/env LD_PRELOAD=/usr/lib/libsb2/libsb2.so.1 /usr/bin/env"
export SB2_RUST_USE_REAL_EXECVP=Yes
export SB2_RUST_USE_REAL_FN=Yes
export SB2_RUST_NO_SPAWNVP=Yes

%ifnarch %ix86
export HOST_CC=host-cc
export HOST_CXX=host-cxx
export CC_i686_unknown_linux_gnu=$HOST_CC
export CXX_i686_unknown_linux_gnu=$HOST_CXX
%endif

# Set meego cross compilers
export PATH=/opt/cross/bin/:$PATH
export CARGO_TARGET_ARMV7_UNKNOWN_LINUX_GNUEABIHF_LINKER=armv7hl-meego-linux-gnueabi-gcc
export CC_armv7_unknown_linux_gnueabihf=armv7hl-meego-linux-gnueabi-gcc
export CXX_armv7_unknown_linux_gnueabihf=armv7hl-meego-linux-gnueabi-g++
export AR_armv7_unknown_linux_gnueabihf=armv7hl-meego-linux-gnueabi-ar
export CARGO_TARGET_AARCH64_UNKNOWN_LINUX_GNU_LINKER=aarch64-meego-linux-gnu-gcc
export CC_aarch64_unknown_linux_gnu=aarch64-meego-linux-gnu-gcc
export CXX_aarch64_unknown_linux_gnu=aarch64-meego-linux-gnu-g++
export AR_aarch64_unknown_linux_gnu=aarch64-meego-linux-gnu-ar

cargo build \
  -j 1 \
  --verbose \
  --release \
  --features=pcre2 \
  --manifest-path %{_sourcedir}/../%{name}-%{version}/Cargo.toml

# << build post

%install
rm -rf %{buildroot}
# >> install pre
# << install pre

# >> install post
%ifarch %arm
targetdir=%{_sourcedir}/../%{name}-%{version}/target/armv7-unknown-linux-gnueabihf/release
%endif
%ifarch aarch64
targetdir=%{_sourcedir}/../%{name}-%{version}/target/aarch64-unknown-linux-gnu/release
%endif
%ifarch %ix86
targetdir=%{_sourcedir}/../%{name}-%{version}/target/i686-unknown-linux-gnu/release
%endif

install -D $targetdir/rg %{buildroot}%{_bindir}/rg

# << install post

%files
# >> files
%defattr(0755,root,root,-)
%{_bindir}/*
# << files
