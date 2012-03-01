## Configuration

In this document you will see reference to `jcurl`. This is a bash shell alias defined in the following manner:

        alias jcurl='curl -H "Content-Type: application/json; charset=utf-8" -g'


## Examples

All results originated from a sample database of real data. 

**Note**

> Examples reference a documented database named `asn_data`. On a Learning Registry Node with the `standards-alignment` design document installed, this database should be `resource_data` unless the node is configured otherwise.


1. All ASN urls for a specific resource url

    jcurl 'http://localhost:5984/asn_data/_design/standards-alignment/_view/discriminator-by-resource?group_level=2&startkey=["http://www.wtamu.edu/academic/anns/mps/math/mathlab/int_algebra/int_alg_tut10_linineq.htm"]&endkey=["http://www.wtamu.edu/academic/anns/mps/math/mathlab/int_algebra/int_alg_tut10_linineq.htm",{}]'


        {"rows":[
            {"key":["http://www.wtamu.edu/academic/anns/mps/math/mathlab/int_algebra/int_alg_tut10_linineq.htm","http://purl.org/ASN/resources/S11434DD"],"value":1},
            {"key":["http://www.wtamu.edu/academic/anns/mps/math/mathlab/int_algebra/int_alg_tut10_linineq.htm","http://purl.org/ASN/resources/S1143635"],"value":1},
            {"key":["http://www.wtamu.edu/academic/anns/mps/math/mathlab/int_algebra/int_alg_tut10_linineq.htm","http://purl.org/ASN/resources/S114363B"],"value":1},
            {"key":["http://www.wtamu.edu/academic/anns/mps/math/mathlab/int_algebra/int_alg_tut10_linineq.htm","http://purl.org/ASN/resources/S1143668"],"value":1},
            {"key":["http://www.wtamu.edu/academic/anns/mps/math/mathlab/int_algebra/int_alg_tut10_linineq.htm","http://purl.org/ASN/resources/S1143677"],"value":1}
        ]}


2. All ASN urls for a specific resource url for some timestamp, or timestamp range

    jcurl 'http://localhost:5984/asn_data/_design/standards-alignment/_view/discriminator-by-resource-ts?group_level=3&startkey=["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894]&endkey=["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894,{}]'

    jcurl 'http://localhost:5984/asn_data/_design/standards-alignment/_view/discriminator-by-resource-ts?group_level=3&startkey=["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225890]&endkey=["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225895,{}]'


        {"rows":[
            {"key":["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894,"http://purl.org/ASN/resources/S114354A"],"value":1},
            {"key":["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894,"http://purl.org/ASN/resources/S11435A3"],"value":1},
            {"key":["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894,"http://purl.org/ASN/resources/S11435A5"],"value":1},
            {"key":["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894,"http://purl.org/ASN/resources/S11435A6"],"value":1},
            {"key":["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894,"http://purl.org/ASN/resources/S11435EC"],"value":1},
            {"key":["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894,"http://purl.org/ASN/resources/S11435F4"],"value":1},
            {"key":["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894,"http://purl.org/ASN/resources/S11435F5"],"value":1},
            {"key":["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894,"http://purl.org/ASN/resources/S11435F7"],"value":1},
            {"key":["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894,"http://purl.org/ASN/resources/S11435FF"],"value":1},
            {"key":["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894,"http://purl.org/ASN/resources/S1143600"],"value":1},
            {"key":["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894,"http://purl.org/ASN/resources/S1143601"],"value":1},
            {"key":["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894,"http://purl.org/ASN/resources/S1143602"],"value":1},
            {"key":["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894,"http://purl.org/ASN/resources/S1143603"],"value":1},
            {"key":["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894,"http://purl.org/ASN/resources/S1143605"],"value":1},
            {"key":["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894,"http://purl.org/ASN/resources/S114360A"],"value":1},
            {"key":["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894,"http://purl.org/ASN/resources/S1143645"],"value":1},
            {"key":["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894,"http://purl.org/ASN/resources/S1143646"],"value":1},
            {"key":["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894,"http://purl.org/ASN/resources/S1143647"],"value":1},
            {"key":["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894,"http://purl.org/ASN/resources/S114364A"],"value":1},
            {"key":["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894,"http://purl.org/ASN/resources/S114364B"],"value":1},
            {"key":["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894,"http://purl.org/ASN/resources/S114364C"],"value":1},
            {"key":["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894,"http://purl.org/ASN/resources/S114364D"],"value":1},
            {"key":["http://www.shodor.org/interactivate/activities/DataFlyer/",1320225894,"http://purl.org/ASN/resources/S114364E"],"value":1}
        ]}


3. All ASNs for a specific resource url prefix

    jcurl 'http://localhost:5984/asn_data/_design/standards-alignment/_view/discriminator-by-resource?group_level=3&startkey=["http://math"]&endkey=["http://math\uD7AF"]'


        {"rows":[
            {"key":["http://math.fullerton.edu/hshultz/mrp/Linear_Equations.PDF","http://purl.org/ASN/resources/S11434E1"],"value":1},
            {"key":["http://math.fullerton.edu/hshultz/mrp/Linear_Equations.PDF","http://purl.org/ASN/resources/S1143539"],"value":1},
            {"key":["http://math.fullerton.edu/hshultz/mrp/Linear_Equations.PDF","http://purl.org/ASN/resources/S114353A"],"value":1},
            {"key":["http://math.fullerton.edu/hshultz/mrp/Linear_Equations.PDF","http://purl.org/ASN/resources/S114353B"],"value":1},
            {"key":["http://math.fullerton.edu/hshultz/mrp/Linear_Equations.PDF","http://purl.org/ASN/resources/S11435EC"],"value":1},
            {"key":["http://math.fullerton.edu/hshultz/mrp/Linear_Equations.PDF","http://purl.org/ASN/resources/S11435ED"],"value":1},
            {"key":["http://math.fullerton.edu/hshultz/mrp/Linear_Equations.PDF","http://purl.org/ASN/resources/S1143602"],"value":1},
            {"key":["http://math.fullerton.edu/hshultz/mrp/Linear_Equations.PDF","http://purl.org/ASN/resources/S1143635"],"value":1},
            {"key":["http://math.fullerton.edu/hshultz/mrp/Linear_Equations.PDF","http://purl.org/ASN/resources/S1143636"],"value":1},
            {"key":["http://math.fullerton.edu/hshultz/mrp/Linear_Equations.PDF","http://purl.org/ASN/resources/S1143642"],"value":1},
            {"key":["http://math.fullerton.edu/hshultz/mrp/Linear_Equations.PDF","http://purl.org/ASN/resources/S114364A"],"value":1},
            {"key":["http://math2.org/math/geometry/areasvols.htm","http://purl.org/ASN/resources/S114351B"],"value":1},
            {"key":["http://math2.org/math/geometry/areasvols.htm","http://purl.org/ASN/resources/S114351D"],"value":1},
            {"key":["http://math2.org/math/geometry/areasvols.htm","http://purl.org/ASN/resources/S1143547"],"value":1},
            {"key":["http://math2.org/math/geometry/areasvols.htm","http://purl.org/ASN/resources/S11435E4"],"value":1},
            {"key":["http://mathforum.org/dr.math/faq/faq.pythagorean.html","http://purl.org/ASN/resources/S1143544"],"value":1},
            {"key":["http://mathforum.org/dr.math/faq/faq.pythagorean.html","http://purl.org/ASN/resources/S1143545"],"value":1},
            {"key":["http://mathforum.org/dr.math/faq/faq.pythagorean.html","http://purl.org/ASN/resources/S1143546"],"value":1},
            {"key":["http://mathforum.org/dr.math/faq/faq.pythagorean.html","http://purl.org/ASN/resources/S11435CE"],"value":1},
            {"key":["http://mathforum.org/dr.math/faq/faq.pythagorean.html","http://purl.org/ASN/resources/S11435D2"],"value":1},
            {"key":["http://mathforum.org/paths/measurement/smile.html","http://purl.org/ASN/resources/S1143460"],"value":1},
            {"key":["http://mathforum.org/paths/measurement/smile.html","http://purl.org/ASN/resources/S1143488"],"value":1},
            {"key":["http://mathforum.org/paths/measurement/smile.html","http://purl.org/ASN/resources/S11434AC"],"value":1},
            {"key":["http://mathforum.org/paths/measurement/smile.html","http://purl.org/ASN/resources/S11434E9"],"value":1},
            {"key":["http://mathforum.org/trscavo/geoboards/","http://purl.org/ASN/resources/S114348B"],"value":1},
            {"key":["http://mathforum.org/trscavo/geoboards/","http://purl.org/ASN/resources/S11434AE"],"value":1},
            {"key":["http://mathforum.org/trscavo/geoboards/","http://purl.org/ASN/resources/S11434E2"],"value":1},
            {"key":["http://mathforum.org/trscavo/geoboards/","http://purl.org/ASN/resources/S114351D"],"value":1},
            {"key":["http://mathforum.org/trscavo/geoboards/","http://purl.org/ASN/resources/S1143545"],"value":1},
            {"key":["http://mathforum.org/trscavo/geoboards/","http://purl.org/ASN/resources/S1143546"],"value":1},
            {"key":["http://mathforum.org/trscavo/geoboards/","http://purl.org/ASN/resources/S114369A"],"value":1},
            {"key":["http://mathforum.org/trscavo/geoboards/","http://purl.org/ASN/resources/S114369B"],"value":1},
            {"key":["http://mathforum.org/trscavo/geoboards/","http://purl.org/ASN/resources/S114369C"],"value":1},
            {"key":["http://mathforum.org/trscavo/geoboards/","http://purl.org/ASN/resources/S114369D"],"value":1}
        ]}


    jcurl 'http://localhost:5984/asn_data/_design/standards-alignment/_view/discriminator-by-resource?group_level=3&startkey=["http://mathforum.org"]&endkey=["http://mathforum.org\uD7AF"]'


        {"rows":[
            {"key":["http://mathforum.org/dr.math/faq/faq.pythagorean.html","http://purl.org/ASN/resources/S1143544"],"value":1},
            {"key":["http://mathforum.org/dr.math/faq/faq.pythagorean.html","http://purl.org/ASN/resources/S1143545"],"value":1},
            {"key":["http://mathforum.org/dr.math/faq/faq.pythagorean.html","http://purl.org/ASN/resources/S1143546"],"value":1},
            {"key":["http://mathforum.org/dr.math/faq/faq.pythagorean.html","http://purl.org/ASN/resources/S11435CE"],"value":1},
            {"key":["http://mathforum.org/dr.math/faq/faq.pythagorean.html","http://purl.org/ASN/resources/S11435D2"],"value":1},
            {"key":["http://mathforum.org/paths/measurement/smile.html","http://purl.org/ASN/resources/S1143460"],"value":1},
            {"key":["http://mathforum.org/paths/measurement/smile.html","http://purl.org/ASN/resources/S1143488"],"value":1},
            {"key":["http://mathforum.org/paths/measurement/smile.html","http://purl.org/ASN/resources/S11434AC"],"value":1},
            {"key":["http://mathforum.org/paths/measurement/smile.html","http://purl.org/ASN/resources/S11434E9"],"value":1},
            {"key":["http://mathforum.org/trscavo/geoboards/","http://purl.org/ASN/resources/S114348B"],"value":1},
            {"key":["http://mathforum.org/trscavo/geoboards/","http://purl.org/ASN/resources/S11434AE"],"value":1},
            {"key":["http://mathforum.org/trscavo/geoboards/","http://purl.org/ASN/resources/S11434E2"],"value":1},
            {"key":["http://mathforum.org/trscavo/geoboards/","http://purl.org/ASN/resources/S114351D"],"value":1},
            {"key":["http://mathforum.org/trscavo/geoboards/","http://purl.org/ASN/resources/S1143545"],"value":1},
            {"key":["http://mathforum.org/trscavo/geoboards/","http://purl.org/ASN/resources/S1143546"],"value":1},
            {"key":["http://mathforum.org/trscavo/geoboards/","http://purl.org/ASN/resources/S114369A"],"value":1},
            {"key":["http://mathforum.org/trscavo/geoboards/","http://purl.org/ASN/resources/S114369B"],"value":1},
            {"key":["http://mathforum.org/trscavo/geoboards/","http://purl.org/ASN/resources/S114369C"],"value":1},
            {"key":["http://mathforum.org/trscavo/geoboards/","http://purl.org/ASN/resources/S114369D"],"value":1}
        ]}


4. All resource urls for a specific ASN


    jcurl 'http://localhost:5984/asn_data/_design/standards-alignment/_view/resource-by-discriminator?group_level=3&startkey=["http://purl.org/ASN/resources/S1143600"]&endkey=["http://purl.org/ASN/resources/S1143600",{}]'


        {"rows":[
            {"key":["http://purl.org/ASN/resources/S1143600","http://www.learner.org/courses/learningmath/algebra/session4/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143600","http://www.math.montana.edu/frankw/ccp/modeling/discrete/linear/learn.htm"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143600","http://www.nctm.org/standards/content.aspx?id=26790"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143600","http://www.shodor.org/interactivate/activities/DataFlyer/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143600","http://www.shodor.org/interactivate/activities/LinearFunctMachine/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143600","http://www.shodor.org/interactivate/activities/MultiFunctionDataFly/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143600","http://www.shodor.org/interactivate/lessons/ReadingGraphs/"],"value":1}
        ]}


5. All resource urls for a specific ASN from Timestamp1 to until Timestamp2

    jcurl 'http://localhost:5984/asn_data/_design/standards-alignment/_view/resource-by-discriminator-ts?group_level=3&startkey=["http://purl.org/ASN/resources/S1143600",1320225894]&endkey=["http://purl.org/ASN/resources/S1143600",1320225896,{}]'


        {"rows":[
            {"key":["http://purl.org/ASN/resources/S1143600",1320225894,"http://www.math.montana.edu/frankw/ccp/modeling/discrete/linear/learn.htm"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143600",1320225894,"http://www.shodor.org/interactivate/activities/DataFlyer/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143600",1320225895,"http://www.shodor.org/interactivate/activities/LinearFunctMachine/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143600",1320225896,"http://www.nctm.org/standards/content.aspx?id=26790"],"value":1}
        ]}


6. All resource urls for an ASN prefix

    jcurl 'http://localhost:5984/asn_data/_design/standards-alignment/_view/resource-by-discriminator?group_level=2&startkey=["http://purl.org/ASN/resources/S114360"]&endkey=["http://purl.org/ASN/resources/S114360\uD7AF",{}]'


        {"rows":[
            {"key":["http://purl.org/ASN/resources/S1143600","http://www.learner.org/courses/learningmath/algebra/session4/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143600","http://www.math.montana.edu/frankw/ccp/modeling/discrete/linear/learn.htm"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143600","http://www.nctm.org/standards/content.aspx?id=26790"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143600","http://www.shodor.org/interactivate/activities/DataFlyer/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143600","http://www.shodor.org/interactivate/activities/LinearFunctMachine/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143600","http://www.shodor.org/interactivate/activities/MultiFunctionDataFly/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143600","http://www.shodor.org/interactivate/lessons/ReadingGraphs/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143601","http://www.math.montana.edu/frankw/ccp/modeling/discrete/linear/learn.htm"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143601","http://www.shodor.org/interactivate/activities/DataFlyer/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143601","http://www.shodor.org/interactivate/activities/MultiFunctionDataFly/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143601","http://www.shodor.org/interactivate/lessons/ReadingGraphs/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143602","http://math.fullerton.edu/hshultz/mrp/Linear_Equations.PDF"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143602","http://www.shodor.org/interactivate/activities/DataFlyer/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143602","http://www.shodor.org/interactivate/activities/Graphit/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143602","http://www.shodor.org/interactivate/activities/MultiFunctionDataFly/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143602","http://www.shodor.org/interactivate/activities/SlopeSlider/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143602","http://www.shodor.org/interactivate/lessons/GraphsAndFunctions/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143602","http://www.shodor.org/interactivate/lessons/ReadingGraphs/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143602","http://www.shodor.org/interactivate/lessons/VerticalLineTest/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143603","http://www.shodor.org/interactivate/activities/DataFlyer/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143603","http://www.shodor.org/interactivate/activities/Graphit/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143603","http://www.shodor.org/interactivate/activities/MultiFunctionDataFly/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143603","http://www.shodor.org/interactivate/activities/SlopeSlider/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143603","http://www.shodor.org/interactivate/lessons/GraphsAndFunctions/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143603","http://www.shodor.org/interactivate/lessons/ReadingGraphs/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143604","http://www.shodor.org/interactivate/activities/Graphit/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143605","http://www.math.montana.edu/frankw/ccp/modeling/discrete/linear/learn.htm"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143605","http://www.shodor.org/interactivate/activities/DataFlyer/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143605","http://www.shodor.org/interactivate/activities/Graphit/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114360A","http://www.shodor.org/interactivate/activities/DataFlyer/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114360A","http://www.shodor.org/interactivate/activities/Graphit/"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114360A","http://www.shodor.org/interactivate/activities/MultiFunctionDataFly/"],"value":1}
        ]}


7. All ASN Resource Locators

    jcurl 'http://localhost:5984/asn_data/_design/standards-alignment/_view/discriminator-by-resource?group_level=1'


        {"rows":[
            {"key":["http://ia.usu.edu/viewproject.php?project=ia:12102"],"value":1},
            {"key":["http://illuminations.nctm.org/LessonDetail.aspx?ID=U159"],"value":2},
            {"key":["http://illuminations.nctm.org/LessonDetail.aspx?ID=U172"],"value":7},
            {"key":["http://illuminations.nctm.org/LessonDetail.aspx?ID=U98"],"value":4},
            {"key":["http://lgfl.skoool.co.uk/content/keystage3/maths/pc/learningsteps/LIELC/LO_Template.swf"],"value":1},
            {"key":["http://library.thinkquest.org/C0110840/dtgraph.htm"],"value":7},
            {"key":["http://mason.gmu.edu/~mmankus/AreaLab/1Sqrect.htm"],"value":5},
            {"key":["http://math.fullerton.edu/hshultz/mrp/Linear_Equations.PDF"],"value":11},
            {"key":["http://math2.org/math/geometry/areasvols.htm"],"value":4},
            {"key":["http://mathforum.org/dr.math/faq/faq.pythagorean.html"],"value":5},
            {"key":["http://mathforum.org/paths/measurement/smile.html"],"value":4},
            {"key":["http://mathforum.org/trscavo/geoboards/"],"value":10},
            {"key":["http://mste.illinois.edu/users/pavel/java/geoboard/"],"value":7},
            {"key":["http://mypages.iit.edu/~smile/ma9509.html"],"value":6},
            {"key":["http://nlvm.usu.edu/en/nav/frames_asid_105_g_2_t_1.html"],"value":4},
            {"key":["http://nlvm.usu.edu/en/nav/frames_asid_164_g_3_t_3.html?open=instructions"],"value":1},
            {"key":["http://perkins.pub30.convio.net/accessiblescience/activities/physical-science-activities/volume-mass-density-boxes.html"],"value":2},
            {"key":["http://resources.sparklebox.me.uk/501-999/sb614.pdf"],"value":4},
            {"key":["http://sln.fi.edu/school/math2/sept.html#measure"],"value":5},
            {"key":["http://sunsite.ubc.ca/LivingMathematics/V001N01/UBCExamples/Pythagoras/pythagoras.html"],"value":2},
            {"key":["http://www.aaamath.com/fra16_x2.htm"],"value":1},
            {"key":["http://www.aaamath.com/fra66mx2.htm"],"value":1},
            {"key":["http://www.aaamath.com/fra66px2.htm"],"value":1},
            {"key":["http://www.algebralab.org/lessons/lesson.aspx?file=Geometry_3Dcylindersprisms.xml"],"value":3},
            {"key":["http://www.algebralab.org/Word/Word.aspx?file=Algebra_InterestI.xml"],"value":1},
            {"key":["http://www.augustatech.edu/math/molik/ConversionWP.pdf"],"value":2},
            {"key":["http://www.cehd.umn.edu/rationalnumberproject/89_3.html"],"value":10},
            {"key":["http://www.cimt.plymouth.ac.uk/projects/mepres/book8/bk8i3/bk8_3i4.htm"],"value":1},
            {"key":["http://www.cmhouston.org/attachments/files/1690/CaterpillarMeasure.pdf"],"value":3},
            {"key":["http://www.compasslearningodyssey.com/sample_act/math_k/grade/subject/mak_04_03_03.html"],"value":1},
            {"key":["http://www.cyberbee.com/henrybuilds/extensions.html"],"value":4},
            {"key":["http://www.evgschool.org/area_and_perimeter_word_problems.htm"],"value":6},
            {"key":["http://www.fi.uu.nl/toepassingen/00022/toepassing_wisweb.en.html"],"value":1},
            {"key":["http://www.fi.uu.nl/toepassingen/00062/toepassing_wisweb.en.html"],"value":3},
            {"key":["http://www.fi.uu.nl/toepassingen/00091/toepassing_wisweb.en.html"],"value":5},
            {"key":["http://www.fi.uu.nl/toepassingen/00146/toepassing_wisweb.en.html"],"value":5},
            {"key":["http://www.fi.uu.nl/toepassingen/00297/toepassing_wisweb.en.html"],"value":1},
            {"key":["http://www.fi.uu.nl/toepassingen/03035/toepassing_wisweb.en.html"],"value":1},
            {"key":["http://www.figurethis.org/challenges/c03/challenge.htm"],"value":3},
            {"key":["http://www.figurethis.org/challenges/c18/challenge.htm"],"value":3},
            {"key":["http://www.figurethis.org/challenges/c47/challenge.htm"],"value":2},
            {"key":["http://www.iit.edu/~smile/ma9517.html"],"value":5},
            {"key":["http://www.instructorweb.com/docs/pdf/convdistance.pdf"],"value":2},
            {"key":["http://www.learner.org/courses/learningmath/algebra/session4/"],"value":10},
            {"key":["http://www.learner.org/courses/learningmath/data/session7/part_c/"],"value":7},
            {"key":["http://www.learner.org/courses/learningmath/number/session9/part_a/"],"value":4},
            {"key":["http://www.learnnc.org/lp/pages/3376?ref=search"],"value":3},
            {"key":["http://www.lessonplanspage.com/MathVolumeDefinitionsAndFormulas8.htm"],"value":2},
            {"key":["http://www.ltsa.org/pdfrules/R_Ruler_Prob-1.pdf"],"value":2},
            {"key":["http://www.math-kitecture.com/floor.htm"],"value":6},
            {"key":["http://www.math.com/school/subject1/lessons/S1U2L1GL.html"],"value":3},
            {"key":["http://www.math.montana.edu/frankw/ccp/modeling/discrete/linear/learn.htm"],"value":11},
            {"key":["http://www.mathplayground.com/MTV/mathtv15.html"],"value":2},
            {"key":["http://www.mathplayground.com/wpdatabase/Geometry1_1.htm"],"value":1},
            {"key":["http://www.mathsisfun.com/fractions_addition.html"],"value":1},
            {"key":["http://www.mathsisfun.com/fractions_subtraction.html"],"value":1},
            {"key":["http://www.mcwdn.org/Decimals/Metric.html"],"value":2},
            {"key":["http://www.nctm.org/standards/content.aspx?id=26773"],"value":5},
            {"key":["http://www.nctm.org/standards/content.aspx?id=26790"],"value":7},
            {"key":["http://www.onlinemathlearning.com/circle-problems.html"],"value":2},
            {"key":["http://www.pbs.org/parents/earlymath/grades_games_timetomove.html"],"value":3},
            {"key":["http://www.pbs.org/teachers/mathline/lessonplans/hsmp/yoyo/yoyo_procedure.shtm"],"value":8},
            {"key":["http://www.pbs.org/wgbh/nova/pyramid/geometry/index.html"],"value":1},
            {"key":["http://www.purplemath.com/modules/ineqlin.htm"],"value":5},
            {"key":["http://www.purplemath.com/modules/ratio.htm"],"value":9},
            {"key":["http://www.regentsprep.org/Regents/math/geometry/GCG1/indexGCG1.htm"],"value":3},
            {"key":["http://www.regentsprep.org/Regents/math/geometry/GP11/PracSimPfs.htm"],"value":2},
            {"key":["http://www.regentsprep.org/Regents/math/geometry/GT3/DActiv.htm"],"value":4},
            {"key":["http://www.shodor.org/interactivate/activities/AdvancedMontyHall/"],"value":7},
            {"key":["http://www.shodor.org/interactivate/activities/AlgebraQuiz/"],"value":8},
            {"key":["http://www.shodor.org/interactivate/activities/ArithmeticFour/"],"value":10},
            {"key":["http://www.shodor.org/interactivate/activities/BasicSpinner/"],"value":9},
            {"key":["http://www.shodor.org/interactivate/activities/ColoringMultiples/"],"value":8},
            {"key":["http://www.shodor.org/interactivate/activities/ConicFlyer/"],"value":5},
            {"key":["http://www.shodor.org/interactivate/activities/DataFlyer/"],"value":23},
            {"key":["http://www.shodor.org/interactivate/activities/Factorize/"],"value":8},
            {"key":["http://www.shodor.org/interactivate/activities/Fire/"],"value":8},
            {"key":["http://www.shodor.org/interactivate/activities/Graphit/"],"value":23},
            {"key":["http://www.shodor.org/interactivate/activities/LinearFunctMachine/"],"value":9},
            {"key":["http://www.shodor.org/interactivate/activities/Marbles/"],"value":12},
            {"key":["http://www.shodor.org/interactivate/activities/MultiFunctionDataFly/"],"value":23},
            {"key":["http://www.shodor.org/interactivate/activities/SlopeSlider/"],"value":12},
            {"key":["http://www.shodor.org/interactivate/activities/SurfaceAreaAndVolume/"],"value":4},
            {"key":["http://www.shodor.org/interactivate/lessons/BarGraphLesson/"],"value":2},
            {"key":["http://www.shodor.org/interactivate/lessons/FindingRemaindersinPascal/"],"value":6},
            {"key":["http://www.shodor.org/interactivate/lessons/GraphsAndFunctions/"],"value":8},
            {"key":["http://www.shodor.org/interactivate/lessons/IdeasLeadProbability/"],"value":8},
            {"key":["http://www.shodor.org/interactivate/lessons/IntroStatistics/"],"value":5},
            {"key":["http://www.shodor.org/interactivate/lessons/MultiplyingFractions/"],"value":5},
            {"key":["http://www.shodor.org/interactivate/lessons/PatternsInFractals/"],"value":5},
            {"key":["http://www.shodor.org/interactivate/lessons/ReadingGraphs/"],"value":11},
            {"key":["http://www.shodor.org/interactivate/lessons/ReplacementProb/"],"value":9},
            {"key":["http://www.shodor.org/interactivate/lessons/SurfaceAreaAndVolume/"],"value":16},
            {"key":["http://www.shodor.org/interactivate/lessons/TreeDiagramsProb/"],"value":7},
            {"key":["http://www.shodor.org/interactivate/lessons/VerticalLineTest/"],"value":4},
            {"key":["http://www.teachengineering.org/view_lesson.php?url=http://www.teachengineering.com/collection/duk_/lessons/duk_tall_mary_less/duk_tall_mary_less.xml"],"value":3},
            {"key":["http://www.teachervision.fen.com/tv/printables/tv00099s2.pdf"],"value":1},
            {"key":["http://www.themathpage.com/alg/simultaneous-equations.htm"],"value":5},
            {"key":["http://www.theteacherscorner.net/printable-worksheets/make-your-own/math-worksheets/basic-math/fractions-equations.php"],"value":4},
            {"key":["http://www.wtamu.edu/academic/anns/mps/math/mathlab/int_algebra/int_alg_tut10_linineq.htm"],"value":5}
        ]}


8. All ASN Resource Locators from Timestamp1 to until Timestamp2

    jcurl 'http://localhost:5984/asn_data/_design/standards-alignment/_view/resource-by-ts?startkey=[1319642044]&endkey=[1319642045,{}]&reduce=false'

        {"total_rows":100,"offset":18,"rows":[
            {"id":"940be1c8c2674569a629c8f13dfd7ff6","key":[1319642044,"http://ia.usu.edu/viewproject.php?project=ia:12102"],"value":null},
            {"id":"898dd53e569346abb67c8e7d4474cc58","key":[1319642044,"http://mypages.iit.edu/~smile/ma9509.html"],"value":null},
            {"id":"fe0e72a6794e46adac1608cd50bb6cee","key":[1319642044,"http://sunsite.ubc.ca/LivingMathematics/V001N01/UBCExamples/Pythagoras/pythagoras.html"],"value":null},
            {"id":"b0b181008b46405b88d6cb6b1cb89b2b","key":[1319642044,"http://www.aaamath.com/fra66mx2.htm"],"value":null},
            {"id":"fb62e36ed5f54ab4b485ada572b89dbb","key":[1319642044,"http://www.aaamath.com/fra66px2.htm"],"value":null},
            {"id":"edb8024418f4464b844f50c6ca24b151","key":[1319642044,"http://www.augustatech.edu/math/molik/ConversionWP.pdf"],"value":null},
            {"id":"897259153c6c4193a525534e0f143091","key":[1319642044,"http://www.evgschool.org/area_and_perimeter_word_problems.htm"],"value":null},
            {"id":"5b8242a741244ff9ac4a65d7111f5e1b","key":[1319642044,"http://www.fi.uu.nl/toepassingen/00297/toepassing_wisweb.en.html"],"value":null},
            {"id":"62a0e974af57497da6c71a20204706fb","key":[1319642044,"http://www.fi.uu.nl/toepassingen/03035/toepassing_wisweb.en.html"],"value":null},
            {"id":"64f2bfee14494a5790f46a82ff52ecf8","key":[1319642044,"http://www.learnnc.org/lp/pages/3376?ref=search"],"value":null},
            {"id":"742462921746404a85cdb666a88f5f2f","key":[1319642044,"http://www.regentsprep.org/Regents/math/geometry/GP11/PracSimPfs.htm"],"value":null},
            {"id":"c80432142c5c40a4ab5ea769a2396890","key":[1319642044,"http://www.shodor.org/interactivate/activities/ColoringMultiples/"],"value":null},
            {"id":"cd1b67fdc6124c6493eb742490059bc0","key":[1319642044,"http://www.shodor.org/interactivate/activities/Graphit/"],"value":null},
            {"id":"7e6cc33af67a452e973965a2ff3529b8","key":[1319642044,"http://www.shodor.org/interactivate/lessons/FindingRemaindersinPascal/"],"value":null},
            {"id":"e6fc7bc4465a48a58ea4e2a5e2418f44","key":[1319642044,"http://www.shodor.org/interactivate/lessons/IdeasLeadProbability/"],"value":null},
            {"id":"f0ab1eda5d66459d803533b9026d26c0","key":[1319642044,"http://www.shodor.org/interactivate/lessons/IntroStatistics/"],"value":null},
            {"id":"894ee07829b84c969ff3a44ce0f7a603","key":[1319642044,"http://www.shodor.org/interactivate/lessons/VerticalLineTest/"],"value":null},
            {"id":"3e83c9b00fdc4d5d9a548bae7c220afe","key":[1319642045,"http://nlvm.usu.edu/en/nav/frames_asid_164_g_3_t_3.html?open=instructions"],"value":null},
            {"id":"bace2a68bbe24c8b97781e6593836725","key":[1319642045,"http://www.fi.uu.nl/toepassingen/00022/toepassing_wisweb.en.html"],"value":null},
            {"id":"5da3efc155bc4ead8249ed556b15c9bb","key":[1319642045,"http://www.fi.uu.nl/toepassingen/00091/toepassing_wisweb.en.html"],"value":null},
            {"id":"3fd5ab79b95b43c298c44607345c0680","key":[1319642045,"http://www.figurethis.org/challenges/c03/challenge.htm"],"value":null},
            {"id":"d444c553810c4be980e8f1adb13d8233","key":[1319642045,"http://www.iit.edu/~smile/ma9517.html"],"value":null},
            {"id":"12f3820d705b4bb684e432636fd1e61f","key":[1319642045,"http://www.ltsa.org/pdfrules/R_Ruler_Prob-1.pdf"],"value":null},
            {"id":"e5108fe2c7814113810f6921f4944a01","key":[1319642045,"http://www.mathsisfun.com/fractions_addition.html"],"value":null},
            {"id":"9f3d3e2fe09d4f3abb46d5de669fe35a","key":[1319642045,"http://www.mathsisfun.com/fractions_subtraction.html"],"value":null},
            {"id":"74fc51003d6745a68d902dcdc0a2691f","key":[1319642045,"http://www.shodor.org/interactivate/activities/BasicSpinner/"],"value":null},
            {"id":"2d3668a014c1448a964cfecef61d8557","key":[1319642045,"http://www.shodor.org/interactivate/activities/Marbles/"],"value":null},
            {"id":"c5d46ec9991b4e05bfaf1abac8f19801","key":[1319642045,"http://www.shodor.org/interactivate/lessons/MultiplyingFractions/"],"value":null},
            {"id":"501096b6f59a41409b746805dd966ceb","key":[1319642045,"http://www.shodor.org/interactivate/lessons/PatternsInFractals/"],"value":null}
        ]}


    jcurl 'http://localhost:5984/asn_data/_design/standards-alignment/_view/resource-by-ts?startkey=[1319642044]&endkey=[1319642045,{}]&group_level=2'

        {"rows":[
            {"key":[1319642044,"http://ia.usu.edu/viewproject.php?project=ia:12102"],"value":1},
            {"key":[1319642044,"http://mypages.iit.edu/~smile/ma9509.html"],"value":1},
            {"key":[1319642044,"http://sunsite.ubc.ca/LivingMathematics/V001N01/UBCExamples/Pythagoras/pythagoras.html"],"value":1},
            {"key":[1319642044,"http://www.aaamath.com/fra66mx2.htm"],"value":1},
            {"key":[1319642044,"http://www.aaamath.com/fra66px2.htm"],"value":1},
            {"key":[1319642044,"http://www.augustatech.edu/math/molik/ConversionWP.pdf"],"value":1},
            {"key":[1319642044,"http://www.evgschool.org/area_and_perimeter_word_problems.htm"],"value":1},
            {"key":[1319642044,"http://www.fi.uu.nl/toepassingen/00297/toepassing_wisweb.en.html"],"value":1},
            {"key":[1319642044,"http://www.fi.uu.nl/toepassingen/03035/toepassing_wisweb.en.html"],"value":1},
            {"key":[1319642044,"http://www.learnnc.org/lp/pages/3376?ref=search"],"value":1},
            {"key":[1319642044,"http://www.regentsprep.org/Regents/math/geometry/GP11/PracSimPfs.htm"],"value":1},
            {"key":[1319642044,"http://www.shodor.org/interactivate/activities/ColoringMultiples/"],"value":1},
            {"key":[1319642044,"http://www.shodor.org/interactivate/activities/Graphit/"],"value":1},
            {"key":[1319642044,"http://www.shodor.org/interactivate/lessons/FindingRemaindersinPascal/"],"value":1},
            {"key":[1319642044,"http://www.shodor.org/interactivate/lessons/IdeasLeadProbability/"],"value":1},
            {"key":[1319642044,"http://www.shodor.org/interactivate/lessons/IntroStatistics/"],"value":1},
            {"key":[1319642044,"http://www.shodor.org/interactivate/lessons/VerticalLineTest/"],"value":1},
            {"key":[1319642045,"http://nlvm.usu.edu/en/nav/frames_asid_164_g_3_t_3.html?open=instructions"],"value":1},
            {"key":[1319642045,"http://www.fi.uu.nl/toepassingen/00022/toepassing_wisweb.en.html"],"value":1},
            {"key":[1319642045,"http://www.fi.uu.nl/toepassingen/00091/toepassing_wisweb.en.html"],"value":1},
            {"key":[1319642045,"http://www.figurethis.org/challenges/c03/challenge.htm"],"value":1},
            {"key":[1319642045,"http://www.iit.edu/~smile/ma9517.html"],"value":1},
            {"key":[1319642045,"http://www.ltsa.org/pdfrules/R_Ruler_Prob-1.pdf"],"value":1},
            {"key":[1319642045,"http://www.mathsisfun.com/fractions_addition.html"],"value":1},
            {"key":[1319642045,"http://www.mathsisfun.com/fractions_subtraction.html"],"value":1},
            {"key":[1319642045,"http://www.shodor.org/interactivate/activities/BasicSpinner/"],"value":1},
            {"key":[1319642045,"http://www.shodor.org/interactivate/activities/Marbles/"],"value":1},
            {"key":[1319642045,"http://www.shodor.org/interactivate/lessons/MultiplyingFractions/"],"value":1},
            {"key":[1319642045,"http://www.shodor.org/interactivate/lessons/PatternsInFractals/"],"value":1}
        ]}

9. All ASNs

    jcurl 'http://localhost:5984/asn_data/_design/standards-alignment/_view/resource-by-discriminator?group_level=1'


        {"rows":[
            {"key":["http://purl.org/ASN/resources/S1143424"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143425"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143426"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143438"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114343A"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114343C"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114343D"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143446"],"value":2},
            {"key":["http://purl.org/ASN/resources/S1143447"],"value":5},
            {"key":["http://purl.org/ASN/resources/S1143449"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114344C"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143454"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114345D"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114345E"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143460"],"value":4},
            {"key":["http://purl.org/ASN/resources/S1143462"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143469"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114346A"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114346B"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114346C"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143477"],"value":2},
            {"key":["http://purl.org/ASN/resources/S114347A"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114347B"],"value":2},
            {"key":["http://purl.org/ASN/resources/S114347C"],"value":2},
            {"key":["http://purl.org/ASN/resources/S114347D"],"value":4},
            {"key":["http://purl.org/ASN/resources/S114347F"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143481"],"value":2},
            {"key":["http://purl.org/ASN/resources/S1143482"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143483"],"value":4},
            {"key":["http://purl.org/ASN/resources/S1143487"],"value":2},
            {"key":["http://purl.org/ASN/resources/S1143488"],"value":2},
            {"key":["http://purl.org/ASN/resources/S1143489"],"value":3},
            {"key":["http://purl.org/ASN/resources/S114348B"],"value":6},
            {"key":["http://purl.org/ASN/resources/S114348D"],"value":3},
            {"key":["http://purl.org/ASN/resources/S114348F"],"value":2},
            {"key":["http://purl.org/ASN/resources/S114349A"],"value":2},
            {"key":["http://purl.org/ASN/resources/S114349B"],"value":2},
            {"key":["http://purl.org/ASN/resources/S114349C"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114349D"],"value":4},
            {"key":["http://purl.org/ASN/resources/S114349E"],"value":4},
            {"key":["http://purl.org/ASN/resources/S11434A2"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11434A4"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11434AA"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11434AC"],"value":3},
            {"key":["http://purl.org/ASN/resources/S11434AD"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11434AE"],"value":7},
            {"key":["http://purl.org/ASN/resources/S11434B0"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11434B1"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11434B3"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11434CE"],"value":3},
            {"key":["http://purl.org/ASN/resources/S11434CF"],"value":2},
            {"key":["http://purl.org/ASN/resources/S11434D1"],"value":3},
            {"key":["http://purl.org/ASN/resources/S11434D2"],"value":3},
            {"key":["http://purl.org/ASN/resources/S11434D4"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11434DB"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11434DC"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11434DD"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11434DE"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11434E1"],"value":6},
            {"key":["http://purl.org/ASN/resources/S11434E2"],"value":5},
            {"key":["http://purl.org/ASN/resources/S11434E3"],"value":2},
            {"key":["http://purl.org/ASN/resources/S11434E5"],"value":3},
            {"key":["http://purl.org/ASN/resources/S11434E6"],"value":2},
            {"key":["http://purl.org/ASN/resources/S11434E7"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11434E8"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11434E9"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11434EA"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11434ED"],"value":3},
            {"key":["http://purl.org/ASN/resources/S11434F2"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11434F5"],"value":3},
            {"key":["http://purl.org/ASN/resources/S11434F9"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11434FA"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11434FC"],"value":2},
            {"key":["http://purl.org/ASN/resources/S11434FF"],"value":2},
            {"key":["http://purl.org/ASN/resources/S114350E"],"value":3},
            {"key":["http://purl.org/ASN/resources/S1143510"],"value":4},
            {"key":["http://purl.org/ASN/resources/S1143513"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143514"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143516"],"value":2},
            {"key":["http://purl.org/ASN/resources/S1143518"],"value":7},
            {"key":["http://purl.org/ASN/resources/S114351B"],"value":3},
            {"key":["http://purl.org/ASN/resources/S114351D"],"value":8},
            {"key":["http://purl.org/ASN/resources/S114351F"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143522"],"value":6},
            {"key":["http://purl.org/ASN/resources/S1143523"],"value":2},
            {"key":["http://purl.org/ASN/resources/S1143531"],"value":7},
            {"key":["http://purl.org/ASN/resources/S1143537"],"value":5},
            {"key":["http://purl.org/ASN/resources/S1143538"],"value":3},
            {"key":["http://purl.org/ASN/resources/S1143539"],"value":4},
            {"key":["http://purl.org/ASN/resources/S114353A"],"value":8},
            {"key":["http://purl.org/ASN/resources/S114353B"],"value":4},
            {"key":["http://purl.org/ASN/resources/S114353D"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114353E"],"value":2},
            {"key":["http://purl.org/ASN/resources/S114353F"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143540"],"value":2},
            {"key":["http://purl.org/ASN/resources/S1143544"],"value":3},
            {"key":["http://purl.org/ASN/resources/S1143545"],"value":3},
            {"key":["http://purl.org/ASN/resources/S1143546"],"value":2},
            {"key":["http://purl.org/ASN/resources/S1143547"],"value":4},
            {"key":["http://purl.org/ASN/resources/S1143549"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114354A"],"value":3},
            {"key":["http://purl.org/ASN/resources/S114354B"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11435A0"],"value":2},
            {"key":["http://purl.org/ASN/resources/S11435A2"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11435A3"],"value":2},
            {"key":["http://purl.org/ASN/resources/S11435A5"],"value":4},
            {"key":["http://purl.org/ASN/resources/S11435A6"],"value":2},
            {"key":["http://purl.org/ASN/resources/S11435A8"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11435A9"],"value":7},
            {"key":["http://purl.org/ASN/resources/S11435AA"],"value":4},
            {"key":["http://purl.org/ASN/resources/S11435AB"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11435AC"],"value":2},
            {"key":["http://purl.org/ASN/resources/S11435AE"],"value":2},
            {"key":["http://purl.org/ASN/resources/S11435AF"],"value":2},
            {"key":["http://purl.org/ASN/resources/S11435B0"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11435B3"],"value":4},
            {"key":["http://purl.org/ASN/resources/S11435B7"],"value":5},
            {"key":["http://purl.org/ASN/resources/S11435B8"],"value":3},
            {"key":["http://purl.org/ASN/resources/S11435B9"],"value":2},
            {"key":["http://purl.org/ASN/resources/S11435BA"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11435BC"],"value":6},
            {"key":["http://purl.org/ASN/resources/S11435BD"],"value":4},
            {"key":["http://purl.org/ASN/resources/S11435BF"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11435C1"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11435C2"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11435C9"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11435CB"],"value":2},
            {"key":["http://purl.org/ASN/resources/S11435CC"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11435CD"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11435CE"],"value":2},
            {"key":["http://purl.org/ASN/resources/S11435CF"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11435D2"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11435DB"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11435DC"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11435DD"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11435DF"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11435E2"],"value":3},
            {"key":["http://purl.org/ASN/resources/S11435E4"],"value":4},
            {"key":["http://purl.org/ASN/resources/S11435E5"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11435E7"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11435E8"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11435E9"],"value":5},
            {"key":["http://purl.org/ASN/resources/S11435EA"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11435EC"],"value":7},
            {"key":["http://purl.org/ASN/resources/S11435ED"],"value":3},
            {"key":["http://purl.org/ASN/resources/S11435EE"],"value":4},
            {"key":["http://purl.org/ASN/resources/S11435F4"],"value":4},
            {"key":["http://purl.org/ASN/resources/S11435F5"],"value":3},
            {"key":["http://purl.org/ASN/resources/S11435F7"],"value":3},
            {"key":["http://purl.org/ASN/resources/S11435F9"],"value":1},
            {"key":["http://purl.org/ASN/resources/S11435FF"],"value":7},
            {"key":["http://purl.org/ASN/resources/S1143600"],"value":7},
            {"key":["http://purl.org/ASN/resources/S1143601"],"value":4},
            {"key":["http://purl.org/ASN/resources/S1143602"],"value":8},
            {"key":["http://purl.org/ASN/resources/S1143603"],"value":6},
            {"key":["http://purl.org/ASN/resources/S1143604"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143605"],"value":3},
            {"key":["http://purl.org/ASN/resources/S114360A"],"value":3},
            {"key":["http://purl.org/ASN/resources/S1143612"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143613"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114362E"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143635"],"value":4},
            {"key":["http://purl.org/ASN/resources/S1143636"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143637"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143639"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114363A"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114363B"],"value":4},
            {"key":["http://purl.org/ASN/resources/S114363E"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143641"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143642"],"value":2},
            {"key":["http://purl.org/ASN/resources/S1143645"],"value":2},
            {"key":["http://purl.org/ASN/resources/S1143646"],"value":2},
            {"key":["http://purl.org/ASN/resources/S1143647"],"value":3},
            {"key":["http://purl.org/ASN/resources/S114364A"],"value":9},
            {"key":["http://purl.org/ASN/resources/S114364B"],"value":4},
            {"key":["http://purl.org/ASN/resources/S114364C"],"value":4},
            {"key":["http://purl.org/ASN/resources/S114364D"],"value":3},
            {"key":["http://purl.org/ASN/resources/S114364E"],"value":4},
            {"key":["http://purl.org/ASN/resources/S114364F"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143650"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114365D"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114365E"],"value":2},
            {"key":["http://purl.org/ASN/resources/S1143660"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143662"],"value":4},
            {"key":["http://purl.org/ASN/resources/S1143663"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143664"],"value":3},
            {"key":["http://purl.org/ASN/resources/S1143665"],"value":2},
            {"key":["http://purl.org/ASN/resources/S1143666"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143667"],"value":2},
            {"key":["http://purl.org/ASN/resources/S1143668"],"value":2},
            {"key":["http://purl.org/ASN/resources/S1143669"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114366A"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114366B"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143677"],"value":2},
            {"key":["http://purl.org/ASN/resources/S114367B"],"value":3},
            {"key":["http://purl.org/ASN/resources/S114367C"],"value":3},
            {"key":["http://purl.org/ASN/resources/S114367D"],"value":4},
            {"key":["http://purl.org/ASN/resources/S114367F"],"value":5},
            {"key":["http://purl.org/ASN/resources/S1143680"],"value":3},
            {"key":["http://purl.org/ASN/resources/S1143681"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143682"],"value":2},
            {"key":["http://purl.org/ASN/resources/S1143683"],"value":3},
            {"key":["http://purl.org/ASN/resources/S1143684"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114368B"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114368D"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143691"],"value":1},
            {"key":["http://purl.org/ASN/resources/S1143692"],"value":2},
            {"key":["http://purl.org/ASN/resources/S114369A"],"value":4},
            {"key":["http://purl.org/ASN/resources/S114369B"],"value":4},
            {"key":["http://purl.org/ASN/resources/S114369C"],"value":8},
            {"key":["http://purl.org/ASN/resources/S114369D"],"value":8},
            {"key":["http://purl.org/ASN/resources/S114369E"],"value":1},
            {"key":["http://purl.org/ASN/resources/S114369F"],"value":3},
            {"key":["http://purl.org/ASN/resources/S11436A0"],"value":2},
            {"key":["http://purl.org/ASN/resources/S11436A1"],"value":2},
            {"key":["http://purl.org/ASN/resources/S11436A2"],"value":2},
            {"key":["http://purl.org/ASN/resources/S11436A3"],"value":3},
            {"key":["http://purl.org/ASN/resources/S11436A4"],"value":1}
        ]}


10. To get "All ASNs from Timestamp1 to until Timestamp2


    jcurl 'http://localhost:5984/asn_data/_design/standards-alignment/_view/discriminator-by-ts?startkey=[1319642045]&endkey=[1319642045,{}]&group_level=2'


        {"rows":[
            {"key":[1319642045,"http://purl.org/ASN/resources/S114343A"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S114343C"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S114343D"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S1143454"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S114347D"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S1143483"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S1143489"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S114349D"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S114349E"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S11434B3"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S11434D1"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S11434E8"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S11434ED"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S11434F5"],"value":2},
            {"key":[1319642045,"http://purl.org/ASN/resources/S11434F9"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S11434FF"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S1143513"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S114351F"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S1143522"],"value":2},
            {"key":[1319642045,"http://purl.org/ASN/resources/S1143523"],"value":2},
            {"key":[1319642045,"http://purl.org/ASN/resources/S1143544"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S1143547"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S11435A8"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S11435A9"],"value":2},
            {"key":[1319642045,"http://purl.org/ASN/resources/S11435AA"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S11435AE"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S11435B7"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S11435B9"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S11435BC"],"value":2},
            {"key":[1319642045,"http://purl.org/ASN/resources/S11435BD"],"value":2},
            {"key":[1319642045,"http://purl.org/ASN/resources/S11435C9"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S11435CB"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S11435CF"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S11435E2"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S11435E4"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S114365D"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S114365E"],"value":2},
            {"key":[1319642045,"http://purl.org/ASN/resources/S1143660"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S1143692"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S11436A0"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S11436A1"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S11436A2"],"value":1},
            {"key":[1319642045,"http://purl.org/ASN/resources/S11436A3"],"value":1}
        ]}

