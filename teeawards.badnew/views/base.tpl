<%namespace name="lib" file="lib.tpl" inheritable="True" />

${lib.header("TeeStats")}

${lib.main_menu(page)}

<div id="lb">
  <div id="rb">
    <div id="mid">
      <div id="container">
        ${next.body()}
      </div>
    </div>
  </div>
</div>

${lib.footer()}
