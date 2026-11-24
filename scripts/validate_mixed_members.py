#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Exercise interleaved definitions and qualified associated array bounds."""
import argparse
import importlib.util
from pathlib import Path

SPEC=importlib.util.spec_from_file_location('members',Path(__file__).with_name('validate_member_annotations.py'))
BASE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(BASE)
TRACKER=r'''enum SlotState { Available; Busy; Consumed; }
struct Tracker {
    #(configurable)
    const WAL_CONCURRENT_CONSUMER_NUMBER: u16 = 5;
    offset: usize;
    buffer_cursor: usize;
    fn capacity(&self) usize { self.buffer.len() }
    buffer_max_offset: usize;
    cursor: usize;
    buffer: [(usize, SlotState); Self::WAL_CONCURRENT_CONSUMER_NUMBER];
    fn new() Tracker {
        Tracker { offset: 0, buffer_cursor: 0, buffer_max_offset: 0, cursor: 0,
            buffer: [(0, SlotState::Available); Self::WAL_CONCURRENT_CONSUMER_NUMBER] }
    }
}
fn main() {
    let tracker = Tracker::new(); print(tracker.capacity());
    #(override: Tracker::WAL_CONCURRENT_CONSUMER_NUMBER=7) {
        let tracker = Tracker::new(); print(tracker.capacity());
    }
    let tracker = Tracker::new(); print(tracker.capacity());
}
'''
ENUM=r'''enum Outcome {
    #(configurable)
    const LIMIT: usize = 3;
    Start;
    fn limit() usize { Self::LIMIT }
    Data { value: i64; };
    End;
    fn value(&self) i64 {
        match self { Outcome::Start => { 0 }, Outcome::Data { value: number } => { number }, Outcome::End => { -1 }, }
    }
}
fn main() {
    let value = Outcome::Data { value: 9 }; print(value.value()); print(Outcome::limit());
    #(override: Outcome::LIMIT=6) { print(Outcome::limit()); }
}
'''
PLAIN=r'''#(configurable)
pub const HEADER: usize = 2;
struct Fixed {
    const SIZE: usize = 3;
    data: [u8; Self::SIZE];
    fn new() Fixed { Fixed { data: [1; Fixed::SIZE] } }
}
fn main() { let value = Fixed::new(); print(value.data.len()); let bytes: [u8; HEADER] = [0; HEADER]; print(bytes.len()); }
'''
SELF=r'''struct Point {
    fn new() Self { Self { value: 7 } }
    value: i64;
}
enum Choice {
    fn new() Self { Self::Data(9) }
    Data(i64);
    End;
    fn number(&self) i64 { match self { Choice::Data(n) => { n }, Choice::End => { 0 }, } }
}
fn main() {
    let point=Point::new(); print(point.value);
    let choice=Choice::new(); print(choice.number());
}
'''
if __name__=='__main__':
    BASE.CASES={'tracker_layout':(TRACKER,'5\n7\n5\n'),'interleaved_enum':(ENUM,'9\n3\n6\n'),'unmarked_qualified_bound':(PLAIN,'3\n2\n'),'definition_self_alias':(SELF,'7\n9\n')}
    BASE.NEGATIVE={'outside_self':'fn bad() Self { 0 } fn main() {}','unknown_bound':'struct X { data: [u8; Self::MISSING]; } fn main() {}','runtime_bound':'fn main() { let size=3; let values:[u8; size]=[0;3]; }'}
    BASE.main()
