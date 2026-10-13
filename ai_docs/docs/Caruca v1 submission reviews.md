

Agency Name:

National Science Foundation

Agency Tracking Number:

2319293

Organization:

NSF Program:

FMitF: Formal Methods in the Field

PI/PD:

Greenberg, Michael

Application Title:

Collaborative Research: FMitF: Track I: Modeling, Learning, and Checking Specifications for Black-Box Shell Components
Review 1

Rating:

Good

Review:

Summary

In the context of the five review elements, please
evaluate the strengths and weaknesses of the proposal with respect to intellectual merit.

Shell programming is ubiquitous, yet the infrastructure to facilitate specification, development, and testing of such programming is lacking. This proposal aims to address this shortcoming. Key topics include formal modeling of commands, inferring and testing of specifications, and tool development.

--Strengths
- Shell program development problem identified in the proposal is important because it is widely used in a broad variety of applications. The problem is challenging because shell commands are black boxes that are composed.
- The proposal outlines details tasks and subtasks. There is not a specific timeline but the task structure looks reasonable.
- PIs have complementary expertise needed to do the proposed research.
- Resources are adequate to conduct the proposed project.

--Weaknesses
- While it is believable that authors will develop and use the necessary formal methods basis for the proposed work, the description itself is short on details on that front.
- Of the subtasks, the synthesis task is less credible than others.
- The tooling section, essential for both evaluation and improving project impact, is less compelling than the others.


In the context of the five review elements, please
evaluate the strengths and weaknesses of the proposal with respect to broader impacts.

--Strengths:
- The problem addressed is important, if tackled successfully, will have a broad impact on shell programming.
- Tooling will enhance the impact.
- Investigators have plans to incorporate results in computer science courses.

--Weaknesses:
- Investigators neither have a track record nor present a discussion of how they would attract underrepresentated populations in their student recruitment or outreach.


Please evaluate the strengths and
weaknesses of the proposal with respect to any additional solicitation-specific review criteria, if
applicable

A key insight guiding the design of our command specification language is that it separates language and argument parsing from description and behavior, using two separate languages. The proposal explains four different ways in which their language will allow specifiers to express commands, though they will begin with an operational version. The ideas of testing to check soundness and completeness are reasonable. Insufficient explanation of a formal approach is a significant weakness.


Summary Statement

A quality proposal that is lacking on the formal methods side.

Review 2

Rating:

Fair

Review:

Summary

In the context of the five review elements, please
evaluate the strengths and weaknesses of the proposal with respect to intellectual merit.

--Strengths

- The proposal describes a formal model for specifying shell commands coupled with techniques and tools for reasoning about those commands that comes out of that model. The technical approach to this sounds feasible and reasonable.

- Shell programs are very hard to reason about; innovations in reasoning about shell programs are likely to advance knowledge in formal methods for reasoning about challenging domains.

- The proposal documents how the PIs are equipped to carry out this research.

--Weaknesses

- The proposed evaluation plan is a bit vague.

In the context of the five review elements, please
evaluate the strengths and weaknesses of the proposal with respect to broader impacts.

--Strengths:

- Shell programs are ubiquitous, so tools for reasoning about them are likely to make a strong impact on other fields if adopted.

- The design of a library of specified shell commands makes adoption a bit more likely.

- The proposal describes how the PIs have a track record of releasing infrastructure for wider use.

--Weaknesses:

- Getting programmers to write specifications of any kind can be very difficult. The proposal would be stronger on broader impacts if it made more of a case for how it will tackle the challenge of adoption.

- The proposal is a bit vague about what fields it hopes to impact beyond formal methods. While shell programs are ubiquitous, the needs and capabilities of shell programmers and users of those programs across domains may not all by identical. The proposal would be strengthened by choosing partners from particular domains and describing a plan for evaluating adoption and usability on those domains.

- There is no credible plan for broadening participation in computing in the proposal. The proposal mentions this exactly once---"our research will also help a more inclusive set of programmers reap the benefits of shell programming"---without elaborating on how that is true. The proposal does not describe any plans for the PIs to carry out any BPC work outside of this.

Please evaluate the strengths and
weaknesses of the proposal with respect to any additional solicitation-specific review criteria, if
applicable

--The extent to which the proposal addresses one or more field areas;

The proposal has the potential to impact downstream fields that use shell programs, but it does not make a strong case for how it will do so.

--The extent to which fundamental contributions to both formal methods and the field area are a likely outcome of this project;

Any work reasoning about shell programs, which are very challenging to reason about, is likely to contribute new insights to formal methods. The proposal is a bit too broad about particular fields they hope to impact, at the cost of concreteness that would make it possible to properly evaluate impacts on downstream fields.

--The extent to which the collaboration plan meets the criteria identified in the solicitation.

The collaboration plan is strong and outlines the expertise the PIs each bring to the project, as well as a concrete plan and timeline for the project. The measures of success for evaluation are a bit vague.

Summary Statement

The proposal is strong on intellectual merits and on contributions to formal methods, but falls short on broader impacts and on contributions to the field. Mainly, it falls short in choosing a specific field to impact, instead casting its net too wide. In doing so, it does not describe sufficiently concrete plans for adoption, which is important given the difficulty of getting programmers and users to adopt any new tools or write specifications. The proposal also does not include any plan for broadening participation in computing. The technical ideas are sound, but more thought is needed to address the deficiencies in broader impacts---the work could be quite impactful given the ubiquity of shell programming, but the proposal does not make a strong enough case for this.

Review 3

Rating:

Good

Review:

Summary

In the context of the five review elements, please
evaluate the strengths and weaknesses of the proposal with respect to intellectual merit.

This proposal aims to provide a new language to formally specify commands used in Shell scripts. The proposal looks to separate out formally specifying the declaration of a command from the behavior of the command. With this language in place, the proposal then aims to ensure that these command specifications are written correctly and package the command specifications into open source toolsets.

***INTELLECTUAL MERIT
--Strengths
- The proposal takes the approach that specifying the command declaration and the command behavior should be two separate activities with two separate languages. This design decision seems well motivated by the examples given in the paper.
- In like with design choice, the proposal outlines different ways to test both the command declaration and the command behavior.

--Weaknesses
- In section 3.1.2, the proposal outlines four different approaches to generating configurations from normalized invocations. The descriptions are clear. However, there is a lot of text space dedicated to this section but what novel activities the proposal will provide down each of these threads is not as clear.
- The proposal outlines that the goal of the activities for Task B is to ensure that the command specifications are correct. The reason for adopting synthesis of command specifications is not clear in the text. In addition, the proposal does not seem to outline what will be used to determine that a synthesized specification is actually correct. Moreover, synthesis is often costly – CEGIS and well as symbolic execution are known to have notable runtime overheads. The expensive of synthesis is not mentioned.
- The proposal does a good job outlining the design decisions for the command specification language, which the research will create and explore. However, task A does not give a strong presentation of what this language might actually look like.

To what extent does the proposed activity suggest and explore creative, original, or potentially transformative concepts?
The proposed work has some novelty in the context of creating a domain-specific specification language for shell commands. The language design takes several best practices, but does not currently outline fundamentally new formal methods mechanisms that would need to be created. However, there is a clear focus on end-user adoption throughout the work, which bodes well for the work producing usable end products that can broaden the use of formal methods within the stated field.

Results of prior NSF support (if applicable):
N/A


In the context of the five review elements, please
evaluate the strengths and weaknesses of the proposal with respect to broader impacts.

***BROADER IMPACTS, including enhancing diversity and integrating research and education:
--Strengths:
- The proposed work has a notable focus on producing open source artifacts for the Shell community, which can help ease the adoption of the proposed work into practice. The proposal outlines different points where datasets and libraries will be produced. In addition, thrust 3 is oriented towards this goal entirely.
- The proposal outlines ways in which the PIs intended to produce educational impacts from the proposed work.

--Weaknesses:
- The proposal does not outline any planned outreach objectives to underrepresented minorities.
- The proposal mentions different areas that can benefit since they make use of shell scripting. It is unclear if their planned open source releases will reach this audience. If so, the proposal could also benefit from an outline of how this community might factor into the evaluation process, or the likelihood these communities would adopt the command specification language.

--Adequacy of Data Management Plan:
The data management plan is adequate.

--Adequacy of Post-doctoral Mentoring Plan (if applicable):
N/A


Please evaluate the strengths and
weaknesses of the proposal with respect to any additional solicitation-specific review criteria, if
applicable

***SOLICITATION-SPECIFIC REVIEW CRITERIA
--The extent to which the proposal addresses one or more field areas;
The proposal identifies systems as its field area with a specific focus on shell scripts and associated tools.

--The extent to which fundamental contributions to both formal methods and the field area are a likely outcome of this project;
Overall, the proposed work, if successful, can have an impact on both the formal methods and field communities.
The formal methods area will benefit from getting another specification language, this time aimed at specifying shell commands. The language is designed with usability in mind, both from the planned tool support as well as the divided structure of the specification language. This can help target a new community of users for formal methods.
The systems/shell area will benefit from a single specification language for commands which can, in turn, both help users appropriately use commands as well as ensure the various transformation tools that already exist are done correctly. The proposal also outlines ways in which the work can help improve documentation of commands.

--The extent to which the collaboration plan meets the criteria identified in the solicitation.
- The proposal and plan identifies a FM PI and a field PI, although both PIs have experience with Shell-based research.
- The collaboration plans lays out a well structured collaborative environment that is largely a virtual environment utilizing many remote work strategies from Covid. The plan also outlines plans to have a loosely co-advised situation for the PhD students funded by the project.
- The plan largely outlines metrics for success although they are not explicitly stated om terms of formal method metrics and separately field metrics. Some of the metrics for success get turned into questions that the work would hope to answer, which would contextualize success but are not themselves direct metrics.


Summary Statement

***SUMMARY STATEMENT
This proposal looks to provide a more formal basis for Shell scripts by focusing on building better support to verify the commands within scripts. The proposal decomposes this perspective into the command invocation and the command behavior.

ADDITIONAL SUGGESTIONS:
The proposal does a nice job outlining the design decisions taken for the specification language, and several of the described research plans indicate a strong focus towards the work being realistically adopted by the scripting community. As a result, the proposal could better motivate the synthesis work.
Sections 3.1.1 and 3.1.2 describe a lot of issues or complications that need to be considered for the designed command specification language. The proposal could benefit from better connecting the proposed work directly to these challenges and how they will be mitigated.
The proposed language the research will build is not entirely clear, although the motivations are. The proposal could further extend the grep example or give some other concrete example to illustrate how the PIs currently plan to bring these design considerations to life.


Justification of rating, including key strengths and critical weaknesses:
Good
This proposal addresses a gap in the current verification support within the shell scripting environment. The proposal could better address the need for expensive interventions like synthesis and provide a clearer picture of what these specification languages would look like.

Review 4

Rating:

Fair

Review:

Summary

In the context of the five review elements, please
evaluate the strengths and weaknesses of the proposal with respect to intellectual merit.

This proposal aims to build tools for modeling (specifying) and reasoning about (Unix) shell scripts and commands. This is an important language that is widely used in may fields, as the PIs point out (p. 5). Specifications of commands, including shell scripts, consist of both syntax and semantics. The PIs "propose to develop (1) a unified formal model of command specifications, (2) associated synthesis and testing techniques for inferring and checking these specifications, and (3) open-source tooling and systems that use this model and techniques to support a variety of use cases---ranging from safety and security monitoring to education" (p. 5).

The proposed work "has three thrusts: (A) a formal model of command specifications with a library of command specifications and open source tooling to manipulate it; (B) a testing discipline to ensure correctness, which supports a black-box and white-box synthesis of command specifications; and (C) further tooling and systems built on our command specifications, for both command developers and end users" (p. 5).

Unfortunately, the details of how this ambitious work would be accomplished are sketchy and have some issues. Most importantly, as the proposers point out, commands vary greatly in their command line argument syntax and in how they parse that, and they vary even more in their possible behaviors. Some command line syntaxes (e.g., for interpreters such as sed and awk) would seem to be only describable using context-sensitive grammars (as they involve jumps to labels), and if the contents of files are included (as in the example of grep -f that the proposers use), then such parsing involves parsing of all programming languages for which there are compilers. The proposal does not make it clear where the syntax of a command is found or even which version of "the shell" is being discussed (sh, bash, csh, or zsh) and does not seem to acknowledge that equivalence for even context-free languages is undecidable.
Second, the effects of commands are so varied (as they include arbitrary code written in Turing-complete programming languages, such as C, and arbitrary system calls), that it would be very difficult to give a coherent semantics to commands and be sure that these semantics were accurate. Because commands could be written in any programming language, the only viable approach to describing the semantics of all possible commands would be a broad semantics paradigm, such as denotational semantics, operational semantics, or algebraic semantics. Verification of the correctness of these descriptions could be reduced to showing the equivalence of type 0 languages, which is clearly undecidable.

So, the proposal wisely concentrates on testing to increase confidence that a description of a command correctly describes that command's behavior (see p. 5 and section 4.1). However, since there are few details on even the approach to giving a semantics to commands, details on testing are quite sketchy. For example, on p. 18, the proposal says that "correctness is contextual: an invocation may be valid in one system state (e.g., some particular file exists) but invalid in another (e.g., some particular file is missing)." However, usually a semantics would be parameterized by such contexts (e.g., in denotational semantics it would be a function that takes as an argument a context such as the state of the file system) or would use some technique to characterize the domain of acceptable initial states (e.g., using preconditions in Hoare Logic). Because such basic properties of the descriptions (semantics) are not made clear, the proposal is not specific about ideas for testing and how they would increase confidence in the accuracy of the descriptions. The tricky issue of isolation of commands being tested for security purposes is mentioned but no concrete plan for dealing with it is given. The tricky issue of commands that loop forever or run out of space is not mentioned. The proposal discusses some alternatives on page 19, but does not come to any conclusions about testing.

There is no plan for evaluation given in the body of the proposal; however, evaluation is discussed in the collaboration plan (p. 61). Unfortunately the plans for evaluation are themselves somewhat sketchy. The plan for evaluation of thrust B mostly consists of a series of questions that could be asked about qualitative and quantitative evaluation. The summary of the evaluation is: "we can measure success in terms of our open source impact" (p. 61).

In contrast to the very ambitious aims of the proposal, which seem to lead to much imprecision, I would advise the proposers to start small. For example consider only commands line arguments as the syntax, ignoring the contents of any files, and assume that the syntax of command line arguments is given by a context-free grammar. Also, to start with, assume that commands only read from stdin and write to stdout or stderr and have an exit code that is an integer that conforms to the convention that 0 means that the command succeeded. Fix a particular shell syntax and give a (say) denotational semantics of its syntax. Decide on how to measure accuracy of a description and devised a testing regimen that increases confidence in that measure and that deals with issues of isolation and errors. Once that is done, continue to make the assumptions weaker and more realistic while explicitly specifying the limitations on what the analysis can accomplish.

PI Greenberg has some prior work on formal semantics for the POSIX shell in POPL 2019 and is the PI whose expertise is in formal methods and programming languages. PI Vasilakis is more of the systems expert and has prior work on "shell-script parallelization and distribution" (p. 60). It would have fit more of the FMitF call to have more about parallelization and distribution in the proposal; as it stands, the proposal concentrates on the formal methods.
Neither PI has had prior NSF support (p. 22).

The resources provided by the PI's universities are adequate for carrying out the work.


In the context of the five review elements, please
evaluate the strengths and weaknesses of the proposal with respect to broader impacts.

As the proposal points out, shell scripts are very widely used in many fields, not just in Computer Science, so the impact of improvements to the correctness and efficiency of the shell could be great.

Broader impacts would also include impacts on industry and on education, by incorporating ideas from the research into courses, as described in section 7 on page 22.

The effect of the proposal on broadening participation in computing is mentioned ("Our research will also help a more inclusive set of programmers reap the benefits of shell programming, avoiding bugs and mistakes when programming via automated reasoning, inference, and analysis--effectively broadening participation in computing and enabling innovation in a variety of fields" (p. 10)), but there is no plan except that somehow by carrying out the research participation will be broadened.


Please evaluate the strengths and
weaknesses of the proposal with respect to any additional solicitation-specific review criteria, if
applicable

The proposal does not say much about the systems side of the research, or offer much detail in how formal methods would be improved, as the details of the descriptions of commands are sketchy and the plan for accuracy improvement is testing.

The PIs have apparently been collaborating previous using virtual meetings. The plan is that: "Collaboration is heavily virtualized, over video conferencing, a shared chat server (Discord), a technical steering committee (TSC) mailing list, and several GitHub repositories under the PaSh project" (p. 60). There are plans for regular meetings, exchanges, and a retreat.


Summary Statement

The need for formal methods to aid tool support for shell scripting is real and important. However, the plans in the proposal are too ambitious and vague to have much confidence in success and are mostly focused on formal semantics, with little in the way of technical ideas in the systems area.
