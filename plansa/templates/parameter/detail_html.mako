<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>
<%block name="title">${_('Parameter')} ${ctx.name}</%block>



<h2>
    ${ctx.name}
</h2>

<table class="table table-nonfluid table-condensed">
    <tr>
        <th>
            GBIF
            <img src="${req.static_url('plansa:static/gbif.png')}"/>
        </th>
        <td>
            <a href="https://www.gbif.org/species/${ctx.id}">${ctx.description}</a>
        </td>
    </tr>
    % if ctx.name_english:
        <tr>
            <th>English</th>
            <td>${ctx.name_english}</td>
        </tr>
    % endif
    % if ctx.name_spanish:
        <tr>
            <th>Spanish</th>
            <td>${ctx.name_spanish}</td>
        </tr>
    % endif
    % if ctx.name_portuguese:
        <tr>
            <th>Portuguese</th>
            <td>${ctx.name_portuguese}</td>
        </tr>
    % endif
</table>

<div style="clear: both"/>
% if map_ or request.map:
${(map_ or request.map).render()}
% endif

${request.get_datatable('values', h.models.Value, parameter=ctx).render()}
