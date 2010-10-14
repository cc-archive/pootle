/*
 * Apertium Service
 */

$(document).ready(function() {
  var target_lang = PTL.editor.normalize_code($("#id_target_f_0").attr("lang"));

  var cookie_name = "apertium_pairs";
  var cookie_options = {path: '/', expires: 15};
  var pairs = $.cookie(cookie_name);
  if (!pairs) {
    pairs = apertium.getSupportedLanguagePairs();
    pairs = $.map(pairs, function(obj, i) {
      return {source: obj.source, target: obj.target};
    });
    var cookie_data = JSON.stringify(pairs);
    $.cookie(cookie_name, cookie_data, cookie_options);
  } else {
    pairs = $.parseJSON(pairs);
  }

  if (PTL.editor.isSupportedTarget(pairs, target_lang)) {
    var sources = $("div.placeholder").prev(".translation-text");
    $(sources).each(function() {
      var source = PTL.editor.normalize_code($(this).attr("lang"));
      if (PTL.editor.isSupportedPair(pairs, source, target_lang)) {
        PTL.editor.addMTButton($(this).parent().siblings().children(".translate-toolbar"),
                             "apertium",
                             m("images/apertium.png"),
                             "Apertium");
      }
    });

    $(".apertium").click(function() {
      var areas = $("[id^=id_target_f_]");
      var sources = $(this).parent().parent().siblings().children(".translation-text");
      var lang_from = PTL.editor.normalize_code(sources.eq(0).attr("lang"));
      var lang_to = PTL.editor.normalize_code(areas.eq(0).attr("lang"));

      // The printf regex based on http://phpjs.org/functions/sprintf:522
      var c_printf_pattern = /%%|%(\d+\$)?([-+\'#0 ]*)(\*\d+\$|\*|\d+)?(\.(\*\d+\$|\*|\d+))?([scboxXuidfegEG])/g;
      var csharp_string_format_pattern = /{\d+(,\d+)?(:[a-zA-Z ]+)?}/g;
      var percent_number_pattern = /%\d+/g;
      var pos = 0;
      var argument_subs = new Array();

      $(sources).each(function(j) {
        var source_text = $(this).text();
        source_text = source_text.replace(c_printf_pattern, PTL.editor.collectArguments);
        source_text = source_text.replace(csharp_string_format_pattern, PTL.editor.collectArguments);
        source_text = source_text.replace(percent_number_pattern, PTL.editor.collectArguments);

        var content = new Object()
        content.text = source_text;
        content.type = "txt";
        apertium.translate(content, lang_from, lang_to, function(result) {
          if (result.translation) {
            var translation = result.translation;
            for (var i=0; i<argument_subs.length; i++)
              translation = translation.replace("__" + i + "__", argument_subs[i]);
            areas.eq(j).val(translation);
            areas.eq(j).focus();
          } else {
            alert("Apertium Error: " + result.error.message);
          }
        });
      });
      PTL.editor.goFuzzy();
      return false;
    });
  }

});
