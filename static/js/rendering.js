function hash(string) {
  var chr;
  var hash = 0;
  if (string.length === 0) return hash;
  for (var i = 0; i < string.length; i++) {
    chr = string.charCodeAt(i);
    hash = (hash << 5) - hash + chr;
    hash |= 0; // Convert to 32bit integer
  }
  return hash;
}

function _norm_link(string) {
  const _norm_chat = s => s.replace(/^chat:\/\/(.+)$/, "");

  const _norm_cindy_link = s =>
    s.replace(domainRegex, "javascript:goto('$1');");

  return _norm_chat(string);
}

function _norm_countdown(string) {
  return string.replace(
    /\/countdown\(([^)]+)\)\//g,
    "<span class='btn disabled countdownobj' until='$1'>CountDownObject</span>"
  );
}

function _norm_tabs(string) {
  var _createID = (text, nmspc) =>
    "tab-" + (nmspc ? nmspc + "-" : "") + hash(text);

  function _build_tabs_navtabs(tab_titles, tab_contents, namespace) {
    var returns = `
<ul class="nav nav-tabs"${namespace ? " id='tabs-" + namespace + "'" : ""}>`;

    for (var i in tab_titles) {
      const newId = _createID(tab_contents[i], namespace);
      returns += `
<li${i == 0 ? " class='active'" : ""} id="nav${newId}">
  <a data-toggle="tab" data-target="#${newId}">
    ${tab_titles[i]}
  </a>
</li>`;
    }

    returns += "</ul>";
    return returns;
  }

  function _build_tabs_contents(tab_titles, tab_contents, namespace) {
    var returns = "<div class='tab-content'>";

    for (var i in tab_titles) {
      returns += `
<div id="${_createID(tab_contents[i], namespace)}"
  ${i == 0 ? "class='tab-pane active'" : "class='tab-pane'"}>
  ${tab_contents[i]}
</div>`;
    }

    returns += "</div>";
    return returns;
  }

  function _build_tabs() {
    var res,
      tab_titles = Array(),
      tab_contents = Array();

    var namespace = arguments[1],
      text = arguments[2],
      returns = text,
      regex = /<!--tab *([^>]*?)-->([\s\S]*?)<!--endtab-->/g;

    while ((res = regex.exec(text))) {
      tab_titles.push(res[1] ? res[1] : "tab");
      tab_contents.push(res[2]);
    }

    return (
      _build_tabs_navtabs(tab_titles, tab_contents, namespace) +
      _build_tabs_contents(tab_titles, tab_contents, namespace)
    );
  }

  return string.replace(
    /<!--tabs ?([^>]*?)-->([\s\S]*?)<!--endtabs-->/g,
    _build_tabs
  );
}

function PreNorm(string) {
  string = _norm_tabs(string);
  return string;
}

function line2md(string) {
  const mdEscape = markdownit({
    html: false,
    breaks: true,
    linkify: true,
    typographer: true
  }).enable(["table", "strikethrough"]);
  string = PreNorm(string);

  return sanitizeHtml(
    mdEscape
      .render(string)
      .replace(/<p>/g, "")
      .replace(/<\/p>\s*$/g, "")
      .replace(/<\/p>/g, '<br style="margin-bottom: 10px" />'),
    {
      allowedTags: false,
      allowedAttributes: false,
      allowedSchemes: ["http", "https", "ftp", "mailto", "chat", "javascript"],
      textFilter: _norm_countdown,
      transformTags: {
        "*": (tagName, attribs) => ({
          tagName,
          attribs: attribs.href
            ? {
                ...attribs,
                href: _norm_link(attribs.href)
              }
            : attribs
        })
      }
    }
  );
}

function text2md(string, safe) {
  const md = markdownit({
    html: true,
    breaks: true,
    linkify: true,
    typographer: true
  }).enable(["table", "strikethrough"]);
  if (safe) {
    return sanitizeHtml(md.render(PreNorm(string)), {
      allowedTags: false,
      allowedAttributes: false,
      allowedSchemes: ["http", "https", "ftp", "mailto", "chat", "javascript"],
      textFilter: _norm_countdown,
      transformTags: {
        "*": (tagName, attribs) => ({
          tagName,
          attribs: attribs.href
            ? {
                ...attribs,
                href: _norm_link(attribs.href)
              }
            : attribs
        })
      }
    });
  } else {
    return sanitizeHtml(md.render(PreNorm(string)), {
      allowedTags: [
        "a",
        "b",
        "big",
        "blockquote",
        "br",
        "caption",
        "center",
        "code",
        "div",
        "em",
        "font",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "hr",
        "i",
        "li",
        "nl",
        "ol",
        "p",
        "pre",
        "small",
        "span",
        "strike",
        "strong",
        "table",
        "tbody",
        "td",
        "th",
        "thead",
        "tr",
        "u",
        "ul"
      ],
      allowedAttributes: {
        "*": [
          "align",
          "background",
          "bgcolor",
          "class",
          "color",
          "data-*",
          "height",
          "href",
          "id",
          "size",
          "style",
          "valign",
          "width"
        ]
      },
      allowedStyles: {
        "*": {
          // Match HEX and RGB
          color: [
            /^[a-z]+$/i,
            /^\#(0x)?[0-9a-f]+$/i,
            /^rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)$/
          ],
          background: [
            /^[a-z]+$/i,
            /^\#(0x)?[0-9a-f]+$/i,
            /^rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)$/
          ],
          "background-color": [
            /^[a-z]+$/i,
            /^\#(0x)?[0-9a-f]+$/i,
            /^rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)$/
          ],
          "text-align": [/^left$/, /^right$/, /^center$/],
          // Match any number with px, em, or %
          "font-size": [/^\d+(px|em|\%)?$/],
          width: [/^\d+(px|em|\%)?$/],
          height: [/^\d+(px|em|\%)?$/],
          padding: [/^.*$/],
          margin: [/^.*$/],
          border: [/^.*$/],
          "padding-left": [/^\d+(px|em|\%)?$/],
          "padding-right": [/^\d+(px|em|\%)?$/],
          "padding-top": [/^\d+(px|em|\%)?$/],
          "padding-bottom": [/^\d+(px|em|\%)?$/],
          "margin-left": [/^\d+(px|em|\%)?$/],
          "margin-right": [/^\d+(px|em|\%)?$/],
          "margin-top": [/^\d+(px|em|\%)?$/],
          "margin-bottom": [/^\d+(px|em|\%)?$/],
          "border-left": [/^\d+(px|em|\%)?$/],
          "border-right": [/^\d+(px|em|\%)?$/],
          "border-top": [/^\d+(px|em|\%)?$/],
          "border-bottom": [/^\d+(px|em|\%)?$/]
        }
      },
      allowedSchemes: ["http", "https", "ftp", "mailto", "chat"],
      nonTextTags: ["style", "script"],
      textFilter: _norm_countdown,
      transformTags: {
        "*": (tagName, attribs) => ({
          tagName,
          attribs: attribs.href
            ? {
                ...attribs,
                href: _norm_link(attribs.href)
              }
            : attribs
        })
      }
    });
  }
}

function changeTabularTab(id) {
  const tabContents = document.getElementById(id).parentElement;
  const navtabContents = document.getElementById(`nav${id}`).parentElement;
  Array.forEach(tabContents.children, child => {
    if (child.id === id) {
      child.setAttribute("class", "tab-pane active");
    } else {
      child.setAttribute("class", "tab-pane");
    }
  });
  Array.forEach(navtabContents.children, child => {
    if (child.id === `nav${id}`) {
      child.setAttribute("class", "active");
    } else {
      child.removeAttribute("class");
    }
  });
}
