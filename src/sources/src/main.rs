mod osbuild {
    mod sandbox_api {
        // use std::os::unix::io::{RawFd};

        struct FdSet {
            fds: Vec<i32>
        }

        impl FdSet {
            fn close(&self) {
            }

            fn steal(&self) {
            }
        }

        pub fn arguments() {
        }

        pub fn exception() {
        }

        pub fn metadata() {
        }
    }
}

fn main() {
    println!("Hello, world!");
}
