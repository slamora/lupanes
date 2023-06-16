from lupanes import get_version


def metadata(request):
    return {
        "version": get_version(),
    }
