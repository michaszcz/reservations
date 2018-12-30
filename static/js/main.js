$(document).ready(function () {
    $('.messages').delay(5000).fadeOut('slow');
    const htmlString = `
<div class="delete-popup">
    <p>Czy jesteś pewny? </p>
    <div class="btn btn-sm btn-outline-info yes">Tak</div>
    <div class="btn btn-sm btn-outline-info no">Nie</div>
</div>`;

    $(".delete-action").click(function (e) {
        e.preventDefault();
        let href = $(this).attr("href");
        $('body').append(htmlString);
        $(".yes").click(function () {
            window.location = href;
        });
        $(".no").click(function () {
            $('.delete-popup').remove();
        });
    });

    $("body>nav ul li a").each(function () {
        let h = $(this).attr('href').split('#', 1)[0];
        if (h === "")
            return;
        if (window.location.pathname.startsWith(h)) {
            $(this).parents("li").addClass("active");
        }
    });
});




