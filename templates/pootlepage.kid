<?xml version="1.0" encoding="utf-8"?>
<include xmlns:py="http://purl.org/kid/ns#">

    <div py:def="header(links, session, baseurl, logo_alttext)" py:strip="True">
        <!-- start header -->
        <div id="nav-access">
            <a href="#nav-main" py:content="links.skip_nav">skip to navigation</a>
<!-- TODO need a switch box -->
            <a href="#switch" py:content="links.switch_language">switch language</a>
        </div>

        <div id="header">
            <div>
                <h1><a href="/" title="${links.home}"><img src="/img/nav_logo.png" height="56" width="261" alt="${logo_alttext}" /></a></h1>
            
                <div id="nav-main" class="yuimenubar">
                  <div class="bd">
                    <ul class="first-of-type">
                        <li class="yuimenubaritem"><a href="${baseurl}" py:content="links.home">Home</a></li>
                        <li class="yuimenubaritem"><a href="${baseurl}projects/" py:content="links.projects">All Languages</a></li>
                        <li class="yuimenubaritem"><a href="${baseurl}languages/" py:content="links.languages">All Projects</a></li>
                        <li class="yuimenubaritem"><a href="${baseurl}doc/${links.doclang}/index.html" py:content="links.doc">Docs &amp; Help</a></li>
                        <span py:if="session.issiteadmin" py:strip="True">
                            <li class="yuimenubaritem"><a href="${baseurl}admin/" py:content="links.admin">Admin</a></li>
                        </span>
                        <span py:if="session.isopen" py:strip="True">
                            <li class="yuimenubaritem"><a href="${baseurl}home/">My account</a></li>
                        </span>
                        <li id="menu-login" class="yuimenubaritem"><a href="#"><span>Log in</span></a></li></ul>
                  </div>
                </div>	
            </div>
        </div>
        <!--TODO
        <h1 py:content="instancetitle">
            Distribution se Pootle
        </h1>
        -->
        <!-- end header -->
    </div>

    <div py:def="footer()" py:strip="True">
        <!-- start footer -->
        <div id="footer">
            <div id="footer-contents">
                <ul class="nav">
                   <li><a href="#">Home</a></li>
                   <li><a href="#">All languages</a></li>
                   <li><a href="#">All projects</a></li>
                   <li><a href="#">Docs &amp; Help</a></li>
                   <li><a href="#">About this Pootle Server</a></li>
                </ul>
            </div>
        </div>
        <!-- end footer -->
    </div>

    <!-- TODO FIXME deprecated! -->
    <div py:def="banner(instancetitle, links, session, uidir, uilanguage, baseurl)" id="banner" lang="$uilanguage" dir="$uidir">
        <h1 py:content="instancetitle">
            Distribution se Pootle
        </h1>
        <div class="side">
            <a href="${baseurl}" py:content="links.home">Home</a> |
            <a href="${baseurl}projects/" py:content="links.projects">All Projects</a> |
            <a href="${baseurl}languages/" py:content="links.languages">All Languages</a>
            <span py:if="session.isopen" py:strip="True"> | <a href="${baseurl}home/" py:content="links.account">My account</a></span>
            <span py:if="session.issiteadmin" py:strip="True"> |
            <a href="${baseurl}admin/" py:content="links.admin">Admin</a> </span> |
            <a href="${baseurl}doc/${links.doclang}/index.html" py:content="links.doc">Docs &amp; Help</a>
        </div>
    </div>

    <div py:def="login_form(username_title, password_title, login_text, register_text, logout_text, session, baseurl, uilanguage)" py:strip="True">
        <!-- start login form -->
        <div py:if="session.isopen" py:strip="True">
            <!--
            TODO FIXME Bug 453247
            <span py:content="XML(session.status)">logged in as <b>somebody</b></span> |
            <a href="${baseurl}?islogout=1" py:content="logout_text">Log Out</a>
            -->
        </div>

        <div py:if="not session.isopen" py:strip="True">
            <form action="/${uilanguage}/login.html" method="post" id="login-form">
                <p><label for="username" py:content="username_title">Username</label> <input type="text" id="username" name="username" /></p>
                <p><label for="password" py:content="password_title">Password</label> <input type="password" id="password" name="password" /></p>
                <p><input type="submit" value="${login_text}" /><input type="submit" value="${register_text}" /></p>
                <input type="hidden" name="islogin" value="true" /> 
            </form>
        </div>
        <!-- end login form -->
    </div>

    <!-- TODO FIXME deprecated! -->
    <div py:def="user_links(links, session, uidir, uilanguage, baseurl, block=None)" id="links" class="sidebar" dir="$uidir" lang="$uilanguage">
        <!--! Account information -->
        <div class="account">
            <div class="side">
                <img src="${baseurl}images/person.png" class="icon" alt="" dir="$uidir" lang="$uilanguage" />
            </div>
            <div class="side" py:if="session.isopen">
                <span py:content="XML(session.status)">logged in as <b>somebody</b></span> |
                <a href="${baseurl}?islogout=1" py:content="links.logout">Log Out</a>
            </div>
            <div class="side" py:if="not session.isopen">
              <a href="${baseurl}login.html" py:content="links.login">Log In</a> |
              <a href="${baseurl}register.html" py:content="links.register">Register</a> |
              <a href="${baseurl}activate.html" py:content="links.activate">Activate</a>
            </div>
        </div>
        <div py:if="block != None" py:replace="block"/>
    </div>

    <!-- TODO FIXME deprecated! -->
    <div py:def="about(aboutlink, uidir, uilanguage, baseurl)" id="about" dir="$uidir" lang="$uilanguage">
        <a href="${baseurl}about.html" py:content="aboutlink">About this Pootle server</a>
    </div>

    <div py:def="translationsummarylegend(legend)" id="translationsummarylegend">
        <div> <img src="/images/green-bar.png" alt="" />${legend.translated}</div>
        <div> <img src="/images/purple-bar.png" alt="" />${legend.fuzzy}</div>
        <div> <img src="/images/red-bar.png" alt="" />${legend.untranslated}</div>
    </div>

    <div py:def="userstatistics(user, statstext, statstitle)" id="userstatistics">
      <h3 class="title" py:content="statstitle">User Statistics</h3>
      <table>
        <tr>
          <th scope="row" py:content="statstext['suggaccepted']">Suggestions Accepted</th>
          <td>${user.suggestionsAcceptedCount()}</td>
        </tr>
        <tr>
          <th scope="row" py:content="statstext['suggpending']">Suggestions Pending</th>
          <td>${user.suggestionsPendingCount()}</td>
        </tr>
        <tr>
          <th scope="row" py:content="statstext['suggreviewed']">Suggestions Reviewed</th>
          <td>${user.suggestionsReviewedCount()}</td>
        </tr>
        <tr>
          <th scope="row" py:content="statstext['submade']">Submissions Made</th>
          <td>${user.submissionsCount()}</td>
        </tr>
      </table>
    </div>

    <!-- TODO FIXME make widemodule -->
    <div py:def="topcontributerstable(topstats, topstatsheading)" class="module first clear topcontributers">
        <div class="hd"><h2 py:contents="topstatsheading">Top Contributors</h2></div>
        <div class="bd">
          <table py:for="stats in topstats">
            <caption py:content="stats['headerlabel']">Top Users</caption>
            <thead>
              <tr>
                <th scope="col" py:content="stats['ranklabel']">Rank</th>
                <th scope="col" py:content="stats['namelabel']">Name</th>
                <th scope="col" py:content="stats['vallabel']">Stat</th>
              </tr>
            </thead>
            <tbody>
              <tr py:for="(num, (name, val)) in enumerate(stats['data'])" class="item item-${num % 2}">
                <td>${num+1}. </td>
                <th scope="row">${name}</th>
                <td>${val}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="ft"></div>
    </div>

</include>
