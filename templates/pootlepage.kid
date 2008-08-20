<?xml version="1.0" encoding="utf-8"?>
<include xmlns:py="http://purl.org/kid/ns#">
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

    <div py:def="topcontributerstable(topstats, topstatsheading)" id="topcontributers" class="topcontributers">
        <h3 py:contents="topstatsheading">Top Contributors</h3>
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

</include>
