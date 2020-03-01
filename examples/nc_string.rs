

use core::char::{decode_utf16, REPLACEMENT_CHARACTER};
use core::fmt;
use core::hash;
use core::iter::{FromIterator, FusedIterator};
use core::ops::Bound::{Excluded, Included, Unbounded};
use core::ops::{self, Add, AddAssign, Index, IndexMut, RangeBounds};
use core::ptr;
use core::str::{lossy, pattern::Pattern};

use crate::borrow::{Cow, ToOwned};
use crate::boxed::Box;
use crate::collections::TryReserveError;
use crate::str::{self, from_boxed_utf8_unchecked, Chars, FromStr, Utf8Error};
use crate::vec::Vec;

pub struct String {
    vec: Vec<u8>,
}

pub struct FromUtf8Error {
    bytes: Vec<u8>,
    error: Utf8Error,
}

pub struct FromUtf16Error(());

impl String {
    pub const fn new() -> String {
        String { vec: Vec::new() }
    }

    pub fn with_capacity(capacity: usize) -> String {
        String { vec: Vec::with_capacity(capacity) }
    }

    pub fn from_str(_: &str) -> String {
        panic!("not available with cfg(test)");
    }

    pub fn from_utf8(vec: Vec<u8>) -> Result<String, FromUtf8Error> {
        match str::from_utf8(&vec) {
            Ok(..) => Ok(String { vec }),
            Err(e) => Err(FromUtf8Error { bytes: vec, error: e }),
        }
    }

    pub fn from_utf8_lossy(v: &[u8]) -> Cow<'_, str> {
        let mut iter = lossy::Utf8Lossy::from_bytes(v).chunks();

        let (first_valid, first_broken) = if let Some(chunk) = iter.next() {
            let lossy::Utf8LossyChunk { valid, broken } = chunk;
            if valid.len() == v.len() {
                debug_assert!(broken.is_empty());
                return Cow::Borrowed(valid);
            }
            (valid, broken)
        } else {
            return Cow::Borrowed("");
        };

        const REPLACEMENT: &str = "\u{FFFD}";

        let mut res = String::with_capacity(v.len());
        res.push_str(first_valid);
        if !first_broken.is_empty() {
            res.push_str(REPLACEMENT);
        }

        for lossy::Utf8LossyChunk { valid, broken } in iter {
            res.push_str(valid);
            if !broken.is_empty() {
                res.push_str(REPLACEMENT);
            }
        }

        Cow::Owned(res)
    }

    pub fn from_utf16(v: &[u16]) -> Result<String, FromUtf16Error> {
        let mut ret = String::with_capacity(v.len());
        for c in decode_utf16(v.iter().cloned()) {
            if let Ok(c) = c {
                ret.push(c);
            } else {
                return Err(FromUtf16Error(()));
            }
        }
        Ok(ret)
    }

    pub fn from_utf16_lossy(v: &[u16]) -> String {
        decode_utf16(v.iter().cloned()).map(|r| r.unwrap_or(REPLACEMENT_CHARACTER)).collect()
    }

    pub fn into_raw_parts(self) -> (*mut u8, usize, usize) {
        self.vec.into_raw_parts()
    }

    pub unsafe fn from_raw_parts(buf: *mut u8, length: usize, capacity: usize) -> String {
        String { vec: Vec::from_raw_parts(buf, length, capacity) }
    }

    pub unsafe fn from_utf8_unchecked(bytes: Vec<u8>) -> String {
        String { vec: bytes }
    }

    pub fn into_bytes(self) -> Vec<u8> {
        self.vec
    }

    pub fn as_str(&self) -> &str {
        self
    }

    pub fn as_mut_str(&mut self) -> &mut str {
        self
    }

    pub fn push_str(&mut self, string: &str) {
        self.vec.extend_from_slice(string.as_bytes())
    }

    pub fn capacity(&self) -> usize {
        self.vec.capacity()
    }

    pub fn reserve(&mut self, additional: usize) {
        self.vec.reserve(additional)
    }

    pub fn reserve_exact(&mut self, additional: usize) {
        self.vec.reserve_exact(additional)
    }

    pub fn try_reserve(&mut self, additional: usize) -> Result<(), TryReserveError> {
        self.vec.try_reserve(additional)
    }

    pub fn try_reserve_exact(&mut self, additional: usize) -> Result<(), TryReserveError> {
        self.vec.try_reserve_exact(additional)
    }

    pub fn shrink_to_fit(&mut self) {
        self.vec.shrink_to_fit()
    }

    pub fn shrink_to(&mut self, min_capacity: usize) {
        self.vec.shrink_to(min_capacity)
    }

    pub fn push(&mut self, ch: char) {
        match ch.len_utf8() {
            1 => self.vec.push(ch as u8),
            _ => self.vec.extend_from_slice(ch.encode_utf8(&mut [0; 4]).as_bytes()),
        }
    }

    pub fn as_bytes(&self) -> &[u8] {
        &self.vec
    }

    pub fn truncate(&mut self, new_len: usize) {
        if new_len <= self.len() {
            assert!(self.is_char_boundary(new_len));
            self.vec.truncate(new_len)
        }
    }

    pub fn pop(&mut self) -> Option<char> {
        let ch = self.chars().rev().next()?;
        let newlen = self.len() - ch.len_utf8();
        unsafe {
            self.vec.set_len(newlen);
        }
        Some(ch)
    }

    pub fn remove(&mut self, idx: usize) -> char {
        let ch = match self[idx..].chars().next() {
            Some(ch) => ch,
            None => panic!("cannot remove a char from the end of a string"),
        };

        let next = idx + ch.len_utf8();
        let len = self.len();
        unsafe {
            ptr::copy(self.vec.as_ptr().add(next), self.vec.as_mut_ptr().add(idx), len - next);
            self.vec.set_len(len - (next - idx));
        }
        ch
    }

    pub fn retain<F>(&mut self, mut f: F)
    where
        F: FnMut(char) -> bool,
    {
        let len = self.len();
        let mut del_bytes = 0;
        let mut idx = 0;

        while idx < len {
            let ch = unsafe { self.get_unchecked(idx..len).chars().next().unwrap() };
            let ch_len = ch.len_utf8();

            if !f(ch) {
                del_bytes += ch_len;
            } else if del_bytes > 0 {
                unsafe {
                    ptr::copy(
                        self.vec.as_ptr().add(idx),
                        self.vec.as_mut_ptr().add(idx - del_bytes),
                        ch_len,
                    );
                }
            }

            idx += ch_len;
        }

        if del_bytes > 0 {
            unsafe {
                self.vec.set_len(len - del_bytes);
            }
        }
    }

    pub fn insert(&mut self, idx: usize, ch: char) {
        assert!(self.is_char_boundary(idx));
        let mut bits = [0; 4];
        let bits = ch.encode_utf8(&mut bits).as_bytes();

        unsafe {
            self.insert_bytes(idx, bits);
        }
    }

    unsafe fn insert_bytes(&mut self, idx: usize, bytes: &[u8]) {
        let len = self.len();
        let amt = bytes.len();
        self.vec.reserve(amt);

        ptr::copy(self.vec.as_ptr().add(idx), self.vec.as_mut_ptr().add(idx + amt), len - idx);
        ptr::copy(bytes.as_ptr(), self.vec.as_mut_ptr().add(idx), amt);
        self.vec.set_len(len + amt);
    }

    pub fn insert_str(&mut self, idx: usize, string: &str) {
        assert!(self.is_char_boundary(idx));

        unsafe {
            self.insert_bytes(idx, string.as_bytes());
        }
    }

    pub unsafe fn as_mut_vec(&mut self) -> &mut Vec<u8> {
        &mut self.vec
    }

    pub fn len(&self) -> usize {
        self.vec.len()
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    pub fn split_off(&mut self, at: usize) -> String {
        assert!(self.is_char_boundary(at));
        let other = self.vec.split_off(at);
        unsafe { String::from_utf8_unchecked(other) }
    }

    pub fn clear(&mut self) {
        self.vec.clear()
    }

    pub fn drain<R>(&mut self, range: R) -> Drain<'_>
    where
        R: RangeBounds<usize>,
    {
        let len = self.len();
        let start = match range.start_bound() {
            Included(&n) => n,
            Excluded(&n) => n + 1,
            Unbounded => 0,
        };
        let end = match range.end_bound() {
            Included(&n) => n + 1,
            Excluded(&n) => n,
            Unbounded => len,
        };

        let self_ptr = self as *mut _;
        let chars_iter = self[start..end].chars();

        Drain { start, end, iter: chars_iter, string: self_ptr }
    }

    pub fn replace_range<R>(&mut self, range: R, replace_with: &str)
    where
        R: RangeBounds<usize>,
    {

        match range.start_bound() {
            Included(&n) => assert!(self.is_char_boundary(n)),
            Excluded(&n) => assert!(self.is_char_boundary(n + 1)),
            Unbounded => {}
        };
        match range.end_bound() {
            Included(&n) => assert!(self.is_char_boundary(n + 1)),
            Excluded(&n) => assert!(self.is_char_boundary(n)),
            Unbounded => {}
        };

        unsafe { self.as_mut_vec() }.splice(range, replace_with.bytes());
    }

    pub fn into_boxed_str(self) -> Box<str> {
        let slice = self.vec.into_boxed_slice();
        unsafe { from_boxed_utf8_unchecked(slice) }
    }
}

impl FromUtf8Error {
    pub fn as_bytes(&self) -> &[u8] {
        &self.bytes[..]
    }

    pub fn into_bytes(self) -> Vec<u8> {
        self.bytes
    }

    pub fn utf8_error(&self) -> Utf8Error {
        self.error
    }
}

impl fmt::Display for FromUtf8Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        fmt::Display::fmt(&self.error, f)
    }
}

impl fmt::Display for FromUtf16Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        fmt::Display::fmt("invalid utf-16: lone surrogate found", f)
    }
}

impl Clone for String {
    fn clone(&self) -> Self {
        String { vec: self.vec.clone() }
    }

    fn clone_from(&mut self, source: &Self) {
        self.vec.clone_from(&source.vec);
    }
}

impl FromIterator<char> for String {
    fn from_iter<I: IntoIterator<Item = char>>(iter: I) -> String {
        let mut buf = String::new();
        buf.extend(iter);
        buf
    }
}

impl<'a> FromIterator<&'a char> for String {
    fn from_iter<I: IntoIterator<Item = &'a char>>(iter: I) -> String {
        let mut buf = String::new();
        buf.extend(iter);
        buf
    }
}

impl<'a> FromIterator<&'a str> for String {
    fn from_iter<I: IntoIterator<Item = &'a str>>(iter: I) -> String {
        let mut buf = String::new();
        buf.extend(iter);
        buf
    }
}

impl FromIterator<String> for String {
    fn from_iter<I: IntoIterator<Item = String>>(iter: I) -> String {
        let mut iterator = iter.into_iter();

        match iterator.next() {
            None => String::new(),
            Some(mut buf) => {
                buf.extend(iterator);
                buf
            }
        }
    }
}

impl<'a> FromIterator<Cow<'a, str>> for String {
    fn from_iter<I: IntoIterator<Item = Cow<'a, str>>>(iter: I) -> String {
        let mut iterator = iter.into_iter();

        match iterator.next() {
            None => String::new(),
            Some(cow) => {
                let mut buf = cow.into_owned();
                buf.extend(iterator);
                buf
            }
        }
    }
}

impl Extend<char> for String {
    fn extend<I: IntoIterator<Item = char>>(&mut self, iter: I) {
        let iterator = iter.into_iter();
        let (lower_bound, _) = iterator.size_hint();
        self.reserve(lower_bound);
        iterator.for_each(move |c| self.push(c));
    }
}

impl<'a> Extend<&'a char> for String {
    fn extend<I: IntoIterator<Item = &'a char>>(&mut self, iter: I) {
        self.extend(iter.into_iter().cloned());
    }
}

impl<'a> Extend<&'a str> for String {
    fn extend<I: IntoIterator<Item = &'a str>>(&mut self, iter: I) {
        iter.into_iter().for_each(move |s| self.push_str(s));
    }
}

impl Extend<String> for String {
    fn extend<I: IntoIterator<Item = String>>(&mut self, iter: I) {
        iter.into_iter().for_each(move |s| self.push_str(&s));
    }
}

impl<'a> Extend<Cow<'a, str>> for String {
    fn extend<I: IntoIterator<Item = Cow<'a, str>>>(&mut self, iter: I) {
        iter.into_iter().for_each(move |s| self.push_str(&s));
    }
}

    feature = "pattern",
    reason = "API not fully fleshed out and ready to be stabilized",
    issue = "27721"
)]
impl<'a, 'b> Pattern<'a> for &'b String {
    type Searcher = <&'b str as Pattern<'a>>::Searcher;

    fn into_searcher(self, haystack: &'a str) -> <&'b str as Pattern<'a>>::Searcher {
        self[..].into_searcher(haystack)
    }

    fn is_contained_in(self, haystack: &'a str) -> bool {
        self[..].is_contained_in(haystack)
    }

    fn is_prefix_of(self, haystack: &'a str) -> bool {
        self[..].is_prefix_of(haystack)
    }
}

impl PartialEq for String {
    fn eq(&self, other: &String) -> bool {
        PartialEq::eq(&self[..], &other[..])
    }
    fn ne(&self, other: &String) -> bool {
        PartialEq::ne(&self[..], &other[..])
    }
}

macro_rules! impl_eq {
    ($lhs:ty, $rhs: ty) => {
        impl<'a, 'b> PartialEq<$rhs> for $lhs {
            fn eq(&self, other: &$rhs) -> bool {
                PartialEq::eq(&self[..], &other[..])
            }
            fn ne(&self, other: &$rhs) -> bool {
                PartialEq::ne(&self[..], &other[..])
            }
        }

        impl<'a, 'b> PartialEq<$lhs> for $rhs {
            fn eq(&self, other: &$lhs) -> bool {
                PartialEq::eq(&self[..], &other[..])
            }
            fn ne(&self, other: &$lhs) -> bool {
                PartialEq::ne(&self[..], &other[..])
            }
        }
    };
}

impl_eq! { String, str }
impl_eq! { String, &'a str }
impl_eq! { Cow<'a, str>, str }
impl_eq! { Cow<'a, str>, &'b str }
impl_eq! { Cow<'a, str>, String }

impl Default for String {
    fn default() -> String {
        String::new()
    }
}

impl fmt::Display for String {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        fmt::Display::fmt(&**self, f)
    }
}

impl fmt::Debug for String {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        fmt::Debug::fmt(&**self, f)
    }
}

impl hash::Hash for String {
    fn hash<H: hash::Hasher>(&self, hasher: &mut H) {
        (**self).hash(hasher)
    }
}

impl Add<&str> for String {
    type Output = String;

    fn add(mut self, other: &str) -> String {
        self.push_str(other);
        self
    }
}

impl AddAssign<&str> for String {
    fn add_assign(&mut self, other: &str) {
        self.push_str(other);
    }
}

impl ops::Index<ops::Range<usize>> for String {
    type Output = str;

    fn index(&self, index: ops::Range<usize>) -> &str {
        &self[..][index]
    }
}
impl ops::Index<ops::RangeTo<usize>> for String {
    type Output = str;

    fn index(&self, index: ops::RangeTo<usize>) -> &str {
        &self[..][index]
    }
}
impl ops::Index<ops::RangeFrom<usize>> for String {
    type Output = str;

    fn index(&self, index: ops::RangeFrom<usize>) -> &str {
        &self[..][index]
    }
}
impl ops::Index<ops::RangeFull> for String {
    type Output = str;

    fn index(&self, _index: ops::RangeFull) -> &str {
        unsafe { str::from_utf8_unchecked(&self.vec) }
    }
}
impl ops::Index<ops::RangeInclusive<usize>> for String {
    type Output = str;

    fn index(&self, index: ops::RangeInclusive<usize>) -> &str {
        Index::index(&**self, index)
    }
}
impl ops::Index<ops::RangeToInclusive<usize>> for String {
    type Output = str;

    fn index(&self, index: ops::RangeToInclusive<usize>) -> &str {
        Index::index(&**self, index)
    }
}

impl ops::IndexMut<ops::Range<usize>> for String {
    fn index_mut(&mut self, index: ops::Range<usize>) -> &mut str {
        &mut self[..][index]
    }
}
impl ops::IndexMut<ops::RangeTo<usize>> for String {
    fn index_mut(&mut self, index: ops::RangeTo<usize>) -> &mut str {
        &mut self[..][index]
    }
}
impl ops::IndexMut<ops::RangeFrom<usize>> for String {
    fn index_mut(&mut self, index: ops::RangeFrom<usize>) -> &mut str {
        &mut self[..][index]
    }
}
impl ops::IndexMut<ops::RangeFull> for String {
    fn index_mut(&mut self, _index: ops::RangeFull) -> &mut str {
        unsafe { str::from_utf8_unchecked_mut(&mut *self.vec) }
    }
}
impl ops::IndexMut<ops::RangeInclusive<usize>> for String {
    fn index_mut(&mut self, index: ops::RangeInclusive<usize>) -> &mut str {
        IndexMut::index_mut(&mut **self, index)
    }
}
impl ops::IndexMut<ops::RangeToInclusive<usize>> for String {
    fn index_mut(&mut self, index: ops::RangeToInclusive<usize>) -> &mut str {
        IndexMut::index_mut(&mut **self, index)
    }
}

impl ops::Deref for String {
    type Target = str;

    fn deref(&self) -> &str {
        unsafe { str::from_utf8_unchecked(&self.vec) }
    }
}

impl ops::DerefMut for String {
    fn deref_mut(&mut self) -> &mut str {
        unsafe { str::from_utf8_unchecked_mut(&mut *self.vec) }
    }
}

pub type ParseError = core::convert::Infallible;

impl FromStr for String {
    type Err = core::convert::Infallible;
    fn from_str(s: &str) -> Result<String, Self::Err> {
        Ok(String::from(s))
    }
}

pub trait ToString {
    fn to_string(&self) -> String;
}

impl<T: fmt::Display + ?Sized> ToString for T {
    default fn to_string(&self) -> String {
        use fmt::Write;
        let mut buf = String::new();
        buf.write_fmt(format_args!("{}", self))
            .expect("a Display implementation returned an error unexpectedly");
        buf.shrink_to_fit();
        buf
    }
}

impl ToString for str {
    fn to_string(&self) -> String {
        String::from(self)
    }
}

impl ToString for Cow<'_, str> {
    fn to_string(&self) -> String {
        self[..].to_owned()
    }
}

impl ToString for String {
    fn to_string(&self) -> String {
        self.to_owned()
    }
}

impl AsRef<str> for String {
    fn as_ref(&self) -> &str {
        self
    }
}

impl AsMut<str> for String {
    fn as_mut(&mut self) -> &mut str {
        self
    }
}

impl AsRef<[u8]> for String {
    fn as_ref(&self) -> &[u8] {
        self.as_bytes()
    }
}

impl From<&str> for String {
    fn from(s: &str) -> String {
        s.to_owned()
    }
}

impl From<&String> for String {
    fn from(s: &String) -> String {
        s.clone()
    }
}

impl From<Box<str>> for String {
    fn from(s: Box<str>) -> String {
        s.into_string()
    }
}

impl From<String> for Box<str> {
    fn from(s: String) -> Box<str> {
        s.into_boxed_str()
    }
}

impl<'a> From<Cow<'a, str>> for String {
    fn from(s: Cow<'a, str>) -> String {
        s.into_owned()
    }
}

impl<'a> From<&'a str> for Cow<'a, str> {
    fn from(s: &'a str) -> Cow<'a, str> {
        Cow::Borrowed(s)
    }
}

impl<'a> From<String> for Cow<'a, str> {
    fn from(s: String) -> Cow<'a, str> {
        Cow::Owned(s)
    }
}

impl<'a> From<&'a String> for Cow<'a, str> {
    fn from(s: &'a String) -> Cow<'a, str> {
        Cow::Borrowed(s.as_str())
    }
}

impl<'a> FromIterator<char> for Cow<'a, str> {
    fn from_iter<I: IntoIterator<Item = char>>(it: I) -> Cow<'a, str> {
        Cow::Owned(FromIterator::from_iter(it))
    }
}

impl<'a, 'b> FromIterator<&'b str> for Cow<'a, str> {
    fn from_iter<I: IntoIterator<Item = &'b str>>(it: I) -> Cow<'a, str> {
        Cow::Owned(FromIterator::from_iter(it))
    }
}

impl<'a> FromIterator<String> for Cow<'a, str> {
    fn from_iter<I: IntoIterator<Item = String>>(it: I) -> Cow<'a, str> {
        Cow::Owned(FromIterator::from_iter(it))
    }
}

impl From<String> for Vec<u8> {
    fn from(string: String) -> Vec<u8> {
        string.into_bytes()
    }
}

impl fmt::Write for String {
    fn write_str(&mut self, s: &str) -> fmt::Result {
        self.push_str(s);
        Ok(())
    }

    fn write_char(&mut self, c: char) -> fmt::Result {
        self.push(c);
        Ok(())
    }
}

pub struct Drain<'a> {
    string: *mut String,
    start: usize,
    end: usize,
    iter: Chars<'a>,
}

impl fmt::Debug for Drain<'_> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.pad("Drain { .. }")
    }
}

unsafe impl Sync for Drain<'_> {}
unsafe impl Send for Drain<'_> {}

impl Drop for Drain<'_> {
    fn drop(&mut self) {
        unsafe {
            let self_vec = (*self.string).as_mut_vec();
            if self.start <= self.end && self.end <= self_vec.len() {
                self_vec.drain(self.start..self.end);
            }
        }
    }
}

impl Iterator for Drain<'_> {
    type Item = char;

    fn next(&mut self) -> Option<char> {
        self.iter.next()
    }

    fn size_hint(&self) -> (usize, Option<usize>) {
        self.iter.size_hint()
    }

    fn last(mut self) -> Option<char> {
        self.next_back()
    }
}

impl DoubleEndedIterator for Drain<'_> {
    fn next_back(&mut self) -> Option<char> {
        self.iter.next_back()
    }
}

impl FusedIterator for Drain<'_> {}
