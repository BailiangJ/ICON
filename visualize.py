
import matplotlib.pyplot as plt
from mermaidlite import compute_warped_image_multiNC
import torch

def show_as_grid(phi):
    data_size = phi.size()[-1]
    plot_phi = data_size * phi.detach().cpu() - .5
    axes = plt.gca()
    axes.set_xlim([-.5,data_size - .5])
    axes.set_ylim([data_size - .5,-.5])
    plt.plot(plot_phi[1], plot_phi[0], linewidth=.1)
    plt.plot(plot_phi[1].transpose(0, 1), plot_phi[0].transpose(0, 1), linewidth=.1)



def visualizeRegistration(net, image_A, image_B, N, path):

    net(image_A, image_B)
    du = (net.phi_AB[:, :, 1:, :-1] - net.phi_AB[:, :, :-1, :-1]).detach().cpu()
    dv = (net.phi_AB[:, :, :-1, 1:] - net.phi_AB[:, :, :-1, :-1]).detach().cpu()
    dA = du[:, 0] * dv[:, 1] - du[:, 1] * dv[:, 0]
    
    plt.figure(dpi=400)
    plt.subplot(3, 2, 1)
    ax = plt.gca()
    ax.axes.xaxis.set_ticks([])
    ax.axes.yaxis.set_ticks([])

    plt.title("Image A")
    plt.imshow(image_A[N, 0].cpu())
    plt.subplot(3, 2, 2)
    ax = plt.gca()
    ax.axes.xaxis.set_ticks([])
    ax.axes.yaxis.set_ticks([])
    plt.title("Image B Warped")
    plt.imshow(net.warped_image_B.detach().cpu()[N, 0])
    show_as_grid(net.phi_AB[N])
    plt.subplot(3, 2, 3)
    ax = plt.gca()
    ax.axes.xaxis.set_ticks([])
    ax.axes.yaxis.set_ticks([])
    plt.title("Image B")
    plt.imshow(image_B[N, 0].cpu())
    
    plt.subplot(3, 2, 4)
    ax = plt.gca()
    ax.set_aspect("equal")
    ax.axes.xaxis.set_ticks([])
    ax.axes.yaxis.set_ticks([])
    plt.title("Composition of Transforms")
    show_as_grid((compute_warped_image_multiNC(net.D_BA, net.phi_AB, net.spacing, 1) + net.phi_AB)[N])
    
    plt.subplot(3, 2, 5)
    plt.title("Area form of PhiAB")
    
    plt.imshow(dA[N])
    plt.colorbar()
    plt.savefig(path)
    plt.clf()
    print("Diffeomorphism Failures per batch")
    print(torch.sum(dA < 0))
    

def visualizeRegistrationCompact(net, image_A, image_B, N):

    net(image_A, image_B)
    
    ax = plt.gca()
    ax.axes.xaxis.set_ticks([])
    ax.axes.yaxis.set_ticks([])
    #plt.title("Image B Warped")
    plt.imshow(net.warped_image_B.detach().cpu()[N, 0])
    show_as_grid(net.phi_AB[N])
