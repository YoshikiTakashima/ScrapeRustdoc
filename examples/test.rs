use std::string::ToString;

struct X {
    a: i32,
}

impl ToString for X {
    fn to_string(&self) -> String {
	return self.a.to_string();
    }
}
 
