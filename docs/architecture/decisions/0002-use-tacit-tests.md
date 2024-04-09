# 2. Use Tacit Tests

Date: 2024-04-09

## Use weird tests to capture tacit knowledge

From [Use weird tests to capture tacit knowledge](https://jmduke.com/posts/essays/weird-tests-tacit-knowledge/)

I compensate my inability to stay focus on tasks I dread by trying to automate as much of it as possible.
A very engineering thing to do.

And yet, I don't see much of that when it comes to checking silly things in most codebases. It took ages for something
as straightforward as `pre-commit` to enter the mainstream scene, and it was so obvious in retrospect.

Why don't we extend that mindset to other, more project-specific things?

Check out `tests/tacit/test_files.py`. It contains a test that checks that all classes in the protocol folder are
subclasses of `typing.Protocol` or `enum.Enum`.

What if a new developer comes along and messes with that folder? That's a warning that they are not expected to
include anything other than Protocols and Enums. Is that easily gameable? Yes, of course.

So is pytest.

The point is that there is a test that reminds you of the tacit expectations in the codebase.

A good mental exercise whenever you're looking at a PR is "could a silly test have caught this?".
Funnily enough, most of these tests are answers from chatGPT. They are not that hard to produce, given the right prompt.

Tacit tests are scripts that exercise your codebase. Use them.
